#!/usr/bin/python
# NOTE: this was tested with python 2.7

import argparse
import logging

import json
import re
import subprocess
import sys
import tempfile
import time
import yaml

logging.basicConfig()

LOG = logging.getLogger(__name__)

class K8sCluster(object):
    def __init__(self, name, kubeconfig):
        self.name = name
        self.kubeconfig = kubeconfig

    def doOp(self, cmdArgsList):
        return subprocess.check_output(["kubectl", "--kubeconfig=" + self.kubeconfig] + cmdArgsList)
        
    def getServices(self, matchStrList=None, namespace=None):
        LOG.debug("[{clus}] Getting services: nameStrs=[{match}], ns={ns}".format(clus=self.name,
                                                                                  match=matchStrList,
                                                                                  ns=namespace))
        if namespace:
            namespaceArgs = ["-n", namespace]
        else:
            namespaceArgs = ["--all-namespaces"]
        svcOut = self.doOp(["get", "svc"] +  namespaceArgs + ["-o", "yaml"])
        svcData = yaml.load(svcOut)
        if matchStrList and len(matchStrList) > 0:
            rtnSvcs = []
            for svc in svcData['items']:
                for matchStr in matchStrList:
                    if re.search(matchStr, svc['metadata']['name']):
                        rtnSvcs.append(svc)
            return rtnSvcs
        else:
            return svcData['items']

    def getSvcEndpoints(self, svcName, namespace):
        LOG.debug("[{clus}] Getting endpoints: svc={svc}, ns={ns}".format(clus=self.name,
                                                                          svc=svcName,
                                                                          ns=namespace))
        epOut = self.doOp(["get", "endpoints", svcName, "-n", namespace, "-o", "yaml"])
        eps = yaml.load(epOut)
        return eps

    def doApply(self, k8sObjs, ns=None):
        '''kubectl apply objects via yaml tempfile'''
        with tempfile.NamedTemporaryFile() as tf:
            yaml.dump(k8sObjs, tf)
            tf.flush()
            nsArgs = []
            if ns:
                nsArgs = ["-n", ns]
            applyResult = self.doOp(["apply", "-f", tf.name] + nsArgs)
            LOG.debug(applyResult)

    def doApplyNs(self, ns):
        '''idempotent ns create with kubectl'''
        nsObj = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": ns
            }
        }
        self.doApply(nsObj)


class MulticlusterSvc(object):
    def __init__(self, svc, endpoint, deployedCluster):
        self.svc = svc
        self.ep = endpoint
        self.deployedCluster = deployedCluster
        self.cleanSvcDef()
        self.cleanSvcEpDef()
        
    def cleanSvcDef(self):
        self.svc['metadata']['annotations'].pop('kubectl.kubernetes.io/last-applied-configuration', None)
        self.svc['metadata'].pop('creationTimestamp', None)
        self.svc['metadata'].pop('resourceVersion', None)
        self.svc['metadata'].pop('selfLink', None)
        self.svc['metadata'].pop('uid', None)
        self.svc['spec'].pop('selector', None)
        self.svc['spec'].pop('clusterIP', None)
        self.svc.pop('status', None)

    def cleanSvcEpDef(self):
        self.ep['metadata'].pop("creationTimestamp", None)
        self.ep['metadata'].pop("resourceVersion", None)
        self.ep['metadata'].pop("selfLink", None)
        self.ep['metadata'].pop("uid", None)
        for addr in self.ep['subsets'][0]['addresses']:
            addr.pop('nodeName', None)
            addr.pop('targetRef', None)

    def name(self):
        return self.svc['metadata']['name']

    def ns(self):
        return self.svc['metadata']['namespace']

    def epIps(self):
        return [addr["ip"] for addr in self.ep['subsets'][0]['addresses'] if addr.get("ip", None)]


def deployClientSvcs(services, clusters):
    for svc in services:
        for clus in clusters:
            if svc.deployedCluster.name != clus.name:
                LOG.debug("Deploying {svc} ({ns}) to {clus}".format(svc=svc.name(),
                                                                    ns=svc.ns(),
                                                                    clus=clus.name))
                nsRes = clus.doApplyNs(svc.ns())
                svcRes = clus.doApply(svc.svc)
                LOG.debug(svcRes)
                LOG.debug(svc.ep)
                epRes = clus.doApply(svc.ep)
                LOG.debug(epRes)


def processClusterCfg(cfgData):
    clusters = []
    services = []
    for clusData in cfgData['clusters']:
        cluster = K8sCluster(clusData['name'], clusData['kubeconfig'])
        clusters.append(cluster)
        for svcData in clusData['services']:
            matchStrList = clusData.get('nameMatches', None)
            ns = svcData.get('namespace', None)
            svcs = cluster.getServices(matchStrList=matchStrList, namespace=ns)
            LOG.debug("Got services for cluster {name}".format(name=clusData['name']))
            for svc in svcs:
                LOG.debug("Processing service {name} (ns={ns})".format(name=svc['metadata']['name'],
                                                                       ns=svc['metadata']['namespace']))
                eps = cluster.getSvcEndpoints(svc['metadata']['name'], svc['metadata']['namespace'])
                mcSvc = MulticlusterSvc(svc, eps, cluster)
                LOG.debug("EPs for svc {name} (ns={ns}): {eps}".format(name=mcSvc.name(),
                    ns=mcSvc.ns(),
                    eps=",".join(mcSvc.epIps())))

                services.append(mcSvc)
    deployClientSvcs(services, clusters)

def main():
    """ Bringup AWS cluster via CCP"""
    parser = argparse.ArgumentParser(
        description='Utility to create k8s selectorless services and endpoints for remote services.')

    parser.add_argument('--clusterSvcCfgFile',
                        required=True,
                        help='Configuration file describing'
                             ' the clusters and mapping of services to match and create.')

    parser.add_argument('--debug',
                        default=False,
                        action='store_true',
                        help='Debug level of output')

    args = parser.parse_args()

    if args.debug:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.INFO)

    with open(args.clusterSvcCfgFile, 'r') as cfgf:
        cfgfile_data = yaml.load(cfgf)

    processClusterCfg(cfgfile_data)


if __name__ == '__main__':
    main()
