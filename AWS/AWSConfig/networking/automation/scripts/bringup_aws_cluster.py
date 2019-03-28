#!/usr/bin/python
# NOTE: this was tested with python 2.7

import argparse
import logging

import json
import re
import requests
from requests.auth import HTTPBasicAuth
import subprocess
import sys
import tempfile
import time
import yaml

logging.basicConfig()

LOG = logging.getLogger(__name__)

region2ami = {
    "us-west-2": "ami-0026e2c00d179a86d"
}

# publicCidrs and privateCidrs are lists
def get_awsSubnets(cidr, publicCidrs, privateCidrs):
    return {
        "subnet": cidr,
        "public_subnets": publicCidrs,
        "private_subnets": privateCidrs
    }

class CcpSession(object):
    def __init__(self, ip, port, username="admin", password=""):
        self.root_url = "https://" + ip + ":" + port
        self.username = username
        self.password = password
        self.session = requests.session()

    def login(self):
        payload = { 'username': self.username, 'password': self.password}
        r = self.session.post(self.root_url + "/2/system/login/",
                         headers={"content-type":"application/x-www-form-urlencoded"},
                         data=payload,
                         verify=False)
        if r.status_code == 200:
            self.token = r.cookies.get("CXAccessToken")

    def get_request_json(self, get_url_subpath):
        try: self.token
        except AttributeError:
            self.login()
        resp = requests.get(self.root_url + get_url_subpath,
                                 headers={"X-Auth-Token": self.token},
                                 verify=False)
        if resp.status_code == 200:
            return json.loads(resp.text)
        else:
            LOG.error("get request failed for url \"{url}\", status: {status}".format(url=self.root_url + get_url_subpath,
                                                                                      status=resp.status_code))
        return None

    def get_aws_provider(self, matchstr):
        providers = self.get_request_json("/v3/providers")
        for prov in providers:
            print "Checking provider " + prov['name']
            if re.search(matchstr, prov['name']):
                print "Found provider " + prov['name'] + " with ID: " + prov['id']
                return prov
        return None

    def get_clusters(self, nameMatchstr=None):
        clusters = self.get_request_json("/v3/clusters/")
        if nameMatchstr:
            rtn_clusters = []
            for cluster in clusters:
                if re.search(nameMatchstr, cluster['name']):
                    rtn_clusters.append(cluster)
            return rtn_clusters
        return clusters

    def get_cluster(self, name):
        clusters = self.get_clusters(name)
        for cluster in clusters:
            if cluster['name'] == name:
                return cluster
        return None

    def create_aws_cluster(self, name, provider, awsSubnets, region, sshKeys,
                           awsRoleArn, numWorkers=2, instanceType="t2.small"):
        ami = region2ami.get(region)
        if not ami:
            print "Couldn't find AMI for the region \"{region}\"".format(region=region)
            return
        payload = json.dumps({
            "provider": provider['id'],
            "vpc_sizing": awsSubnets,
            "region": region,
            "type": "eks",
            "ami": ami,
            "instance_type": instanceType,
            "worker_count": numWorkers,
            "access_role_arn": awsRoleArn,
            "name": name,
            "ssh_keys": sshKeys
        })
        print "Payload for the cluster create {payload}".format(payload=payload)
        r = self.session.post(self.root_url + "/v3/clusters/",
                         headers={"X-Auth-Token": self.token},
                         data=payload,
                         verify=False)
        if r.status_code == 200:
            print "Successfully created cluster " + name
        else:
            print r.text

    def wait_for_cluster_state(self, name, state='READY', timeout_s=300, sample_time=30):
        timeleft = timeout_s
        while timeleft > 0:
            cluster = self.get_cluster(name)
            if not cluster:
                return None
            if cluster['status'] == state:
                return state
            time.sleep(sample_time)
        return "TIMEOUT"

    def create_cluster_kubeconfig(self, cluster_nm, kubeconfig_filenm):
        cluster = self.get_cluster(cluster_nm)
        with open(kubeconfig_filenm, 'w') as f:
            f.write(cluster['kubeconfig'])


def validateClusterCfg(clusterCfg):
    if not clusterCfg.get("name"):
        LOG.error("Cluster Config file missing cluster name")
        return False
    if not clusterCfg.get("subnet"):
        LOG.error("Cluster Config file missing cluster subnet")
        return False
    if (not clusterCfg["subnet"].get('cidr')) or \
       not clusterCfg["subnet"].get('publicCidrs') or \
       not clusterCfg["subnet"].get('privateCidrs'):
        LOG.error("Cluster Config file missing cluster subnet info--required keys [ cidr, publicCidrs, privateCidrs ]")
        return False
    if not clusterCfg.get('role_arn_name'):
        LOG.error("Cluster Config file missing cluster 'role_arn_name'")
        return False
    if not clusterCfg.get('ssh_keys'):
        LOG.error("Cluster Config file missing cluster 'ssh_keys' (list)")
        return False

    return True

def findClusterCfgData(clusterCfg):
    if not clusterCfg.get('aws_role_arn'):
        role_nm = clusterCfg.get('role_arn_name')
        if role_nm:
            iam_roles = subprocess.check_output(["aws", "iam", "list-roles"])
            roles = json.loads(iam_roles)
            for role in roles['Roles']:
                if re.search(role_nm, role['Arn']):
                    clusterCfg['aws_role_arn'] = role['Arn']
                    break

    if not clusterCfg.get('region'):
        clusterCfg['region'] = subprocess.check_output(["aws", "configure", "get", "region"]).strip()

def awsEksDisableSNAT(kubeconfig):
    # reference: https://docs.aws.amazon.com/eks/latest/userguide/external-snat.html
    awsNodeDaemonsetJson = subprocess.check_output(["kubectl", "--kubeconfig="+kubeconfig, "get", "daemonset", "-n", "kube-system", "aws-node", "-o", "json"])
    awsNodeDaemonset = json.loads(awsNodeDaemonsetJson)
    for cntnr in awsNodeDaemonset["spec"]["template"]["spec"]["containers"]:
        if cntnr['name'] == 'aws-node':
            env = cntnr.get('env')
            foundSnat = False
            if env:
                for envItem in env:
                    if envItem['name'] == 'AWS_VPC_K8S_CNI_EXTERNALSNAT':
                        foundSnat = True
                        envItem['value'] = "true"
                if not foundSnat:
                    env.append({'name': 'AWS_VPC_K8S_CNI_EXTERNALSNAT', 'value': 'true'})
            break
        else:
            return "ERROR: Unable to disable SNAT due to not finding `aws-node` container in daemonset"
    with tempfile.NamedTemporaryFile() as tf:
        json.dump(awsNodeDaemonset, tf)
        tf.flush()
        replResult = subprocess.check_output(["kubectl", "--kubeconfig="+kubeconfig, "replace", "-n", "kube-system", "-f", tf.name])
    return replResult

def main():
    """ Bringup AWS cluster via CCP"""
    LOG.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description='Utility to bringup AWS clusters via CCP')

    parser.add_argument('--ccpIp',
                        required=True,
                        help='IP for CCP webUI to use.')

    parser.add_argument('--ccpPort',
                        default=443,
                        help='Port for CCP webUI to use.')

    parser.add_argument('--ccpPassword',
                        required=True,
                        help='Password to use for login to  CCP webUI.')

    parser.add_argument('--providerStr',
                        required=True,
                        help='String to find the CCP provider to use.')
    parser.add_argument('--clusterCfgFile',
                        required=True,
                        help='Configuration file describing'
                             ' the cluster to create.')
    parser.add_argument('--debug',
                        default=False,
                        action='store_true',
                        help='Debug level of output')

    parser.add_argument('--skipCreate',
                        default=False,
                        action='store_true',
                        help='Skip the actual cluster create step--redo the post create setup.')

    args = parser.parse_args()

    #if not args.clusterCfgFile or not args.ccpIp or not args.ccpPort or not args.ccpPassword or not args.providerStr:
    #    parser.help()
    
    with open(args.clusterCfgFile, 'r') as cfgf:
        cfgfile_data = yaml.load(cfgf)

    if not validateClusterCfg(cfgfile_data):
        print "Need to fixup the clusterCfgFile"
        sys.exit(1)

    findClusterCfgData(cfgfile_data)

    awsSubnets = get_awsSubnets(cfgfile_data['subnet']['cidr'],
                                cfgfile_data['subnet']['publicCidrs'],
                                cfgfile_data['subnet']['privateCidrs'])
    ccpSession = CcpSession(ip=args.ccpIp, port=args.ccpPort, password=args.ccpPassword)
    awsProvider = ccpSession.get_aws_provider(args.providerStr)
    if not args.skipCreate:
        ccpSession.create_aws_cluster(cfgfile_data['name'], awsProvider, awsSubnets,
                                      cfgfile_data['region'], cfgfile_data['ssh_keys'],
                                      cfgfile_data['aws_role_arn'])

    if ccpSession.wait_for_cluster_state(cfgfile_data['name']) == 'READY':
        print "Cluster ready, creating kubeconfig"
        kubeconf_file = cfgfile_data.get('kubeconf_file')
        if kubeconf_file:
            ccpSession.create_cluster_kubeconfig(cfgfile_data['name'], kubeconf_file)

            enable_snat = cfgfile_data.get('enable_snat')
            if not enable_snat:
                print "Disabling EKS SNAT"
                print awsEksDisableSNAT(kubeconf_file)
            
            apply_manifests = cfgfile_data.get('apply_manifests')
            if apply_manifests:
                for manifest in apply_manifests:
                    print "Applying manifest {manifest}".format(manifest=manifest)
                    apply_res = subprocess.check_output(["kubectl", "--kubeconfig="+kubeconf_file, "apply", "-f", manifest])
                    print apply_res
    else:
        print "Cluster status didn't reach ready"
    print "---looks like we're done---"

if __name__ == '__main__':
    main()
