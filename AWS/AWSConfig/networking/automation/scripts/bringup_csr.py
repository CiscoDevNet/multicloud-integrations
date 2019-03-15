#!/usr/bin/python
# NOTE: this was tested with python 2.7

import argparse
import logging

import json
import os
import re
import requests
from requests.auth import HTTPBasicAuth
import subprocess
import sys
import time
import yaml

logging.basicConfig()

LOG = logging.getLogger(__name__)


def do_cmd(argsList):
    LOG.debug("running command: {cmd}".format(cmd=" ".join(argsList)))
    try:
        cmd_out = subprocess.check_output(argsList)
        print cmd_out
    except subprocess.CalledProcessError as e:
        print "ERROR running command \'{cmd}\': {out}".format(out=e.output, cmd=" ".join(argsList))
    return cmd_out

def validateDmvpnCfg(cmvpnCfg):
    # do some validation that the right keys,values are present
    return True

def buildCsrCommandArgs(vpc_name, sshKey, onprem_cidr, onprem_podcidr, dmvpncfg_data):
    if not validateDmvpnCfg(dmvpncfg_data):
        return None

    cmdArgs = [
        "--stack-prefix="+vpc_name,
        "--key="+sshKey,
        "--on-prem-cidr="+onprem_cidr,
        "--onPremPodCidr="+onprem_podcidr,
    ]
    if dmvpncfg_data.get('InstanceType'):
        cmdArgs.append("--instanceType="+dmvpncfg_data.get('InstanceType'))
    if dmvpncfg_data.get('InboundSSH'):
        cmdArgs.append("--inboundSsh="+dmvpncfg_data.get('InboundSSH'))
    if dmvpncfg_data.get('ike_keyring_peer') and dmvpncfg_data['ike_keyring_peer'].get('ip_range'):
        if dmvpncfg_data['ike_keyring_peer']['ip_range'].get('start'):
            cmdArgs.append("--ikePeerIpStart="+dmvpncfg_data['ike_keyring_peer']['ip_range']['start'])        
        if dmvpncfg_data['ike_keyring_peer']['ip_range'].get('end'):
            cmdArgs.append("--ikePeerIpEnd="+dmvpncfg_data['ike_keyring_peer']['ip_range']['end'])

    cmdArgs.append("--ikePreSharedKey="+dmvpncfg_data['ike_keyring_peer']['pre-shared-key'])
    cmdArgs.append("--ikeRemotePeerIp="+dmvpncfg_data['ike_profile']['remote_peer_ip'])
    cmdArgs.append("--dmvpnIp="+dmvpncfg_data['DmvpnIp'])
    cmdArgs.append("--dmvpnNetmask="+dmvpncfg_data['DmvpnNetmask'])
    cmdArgs.append("--nhrpKey="+dmvpncfg_data['nhrp']['key'])
    cmdArgs.append("--nhrpHubTunnelIp="+dmvpncfg_data['nhrp']['HubTunnelIP'])
    if dmvpncfg_data.get('ospf') and dmvpncfg_data['ospf'].get('processId'):
        cmdArgs.append("--ospfProcId=" + str(dmvpncfg_data['ospf']['processId']))
    cmdArgs.append("--ospfAuthKey="+dmvpncfg_data['ospf']['authKey'])
    cmdArgs.append("--ospfTunnelNetIp="+dmvpncfg_data['ospf']['tunnelNetwork'])
    cmdArgs.append("--ospfTunnelWildcard="+dmvpncfg_data['ospf']['tunnelWildcard'])
    cmdArgs.append("--ospfVpcArea=" + str(dmvpncfg_data['ospf']['vpcArea']))
    cmdArgs.append("--ospfTunnelArea=" + str(dmvpncfg_data['ospf']['tunnelArea']))

    return cmdArgs

def find_vpc(matchstr):
    vpcs_out = do_cmd(["aws", "ec2", "describe-vpcs"])
    vpcs = json.loads(vpcs_out)
    for vpc in vpcs['Vpcs']:
        if vpc.get('Tags'):
            for tag in vpc['Tags']:
                if tag['Key'] == 'Name' and matchstr in tag['Value']:
                    #print vpc['VpcId']
                    return vpc
    return None

def get_csr_instance(vpc):
    csr_inst_out = do_cmd(["aws", "ec2", "describe-instances",
                           "--filters",
                           "Name=vpc-id,Values=" + vpc['VpcId'],
                           "Name=tag:Name,Values=*csr*"])
    csr_inst = json.loads(csr_inst_out)
    for inst in csr_inst['Reservations'][0]['Instances']:
        for tag in inst['Tags']:
            if tag['Key'] == 'Name' and 'csr' in tag['Value']:
                return inst
    return None

def get_csr_eni(vpc, intfNameMatch):
    csr_inst = get_csr_instance(vpc)
    csr_instId = csr_inst['InstanceId']
    csr_enis_out = do_cmd(["aws", "ec2", "describe-network-interfaces",
                           "--filters",
                           "Name=vpc-id,Values=" + vpc['VpcId'],
                           "Name=attachment.instance-id,Values=" + csr_instId])
    enis = json.loads(csr_enis_out)
    for eni in enis['NetworkInterfaces']:
        if eni.get('Attachment') and eni['Attachment'].get('InstanceId') and eni['Attachment']['InstanceId'] == csr_instId:
            if eni.get('TagSet'):
                for tag in eni['TagSet']:
                    if tag['Key'] == 'Name' and intfNameMatch in tag['Value']:
                        return eni
    return None

def find_subnets(vpc, subnetMatchStr):
    subnets_out = do_cmd(["aws", "ec2", "describe-subnets",
                          "--filters", "Name=vpc-id,Values=" + vpc['VpcId'],
                          "Name=tag:Name,Values=" + subnetMatchStr])
    subnets = json.loads(subnets_out)
    return subnets['Subnets']

def find_routeTable_by_subnet(vpc, subnetId):
    route_table_out = do_cmd(["aws", "ec2", "describe-route-tables",
                              "--filters",
                              "Name=association.subnet-id,Values=" + subnetId])
    route_table = json.loads(route_table_out)
    return route_table['RouteTables'][0]

def create_pod_network_routes(vpcNamePrefix, podNetworkCidr):
    vpc = find_vpc(vpcNamePrefix)
    csr_priv_eni = get_csr_eni(vpc, "private")
    subnets = find_subnets(vpc, "*private*")
    for subnet in subnets:
        route_table = find_routeTable_by_subnet(vpc, subnet['SubnetId'])
        create = do_cmd(["aws", "ec2", "create-route",
                         "--destination-cidr-block", podNetworkCidr,
                         "--network-interface-id", csr_priv_eni['NetworkInterfaceId'],
                         "--route-table-id", route_table['RouteTableId']])
        

def main():
    """ Bringup CSR in AWS cluster created via CCP"""
    LOG.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description='Utility to bringup AWS clusters via CCP')

    parser.add_argument('--vpcNamePrefix',
                        required=True,
                        help='String used to find the VPC to create the CSR in.')

    parser.add_argument('--sshKey',
                        required=True,
                        help='ssh key to use for instances created.')

    parser.add_argument('--onPremCidr',
                        required=True,
                        help='CIDR for the OnPremises network.')

    parser.add_argument('--onPremPodCidr',
                        required=True,
                        help='CIDR for the OnPremises network.')

    parser.add_argument('--clusterCfgFile',
                        required=True,
                        help='Configuration file describing'
                             ' the CCP cluster.')
    parser.add_argument('--dmvpnCfgFile',
                        required=True,
                        help='Configuration file describing'
                             ' the DMVPN setup for the on-prem CCP cluster.')
    parser.add_argument('--routes_only',
                        default=False,
                        action='store_true',
                        help='only create routes for pod networks (don\'t do the CSR bringup).')
    
    parser.add_argument('--debug',
                        default=False,
                        action='store_true',
                        help='Debug level of output')

    args = parser.parse_args()

    with open(args.clusterCfgFile, 'r') as cfgf:
        cfgfile_data = yaml.load(cfgf)

    with open(args.dmvpnCfgFile, 'r') as cfgf:
        dmvpncfg_data = yaml.load(cfgf)

    csrCmdArgs = buildCsrCommandArgs(args.vpcNamePrefix,
                                     args.sshKey,
                                     args.onPremCidr,
                                     args.onPremPodCidr,
                                     dmvpncfg_data)
    # for now just call the bash script with the right args
    print csrCmdArgs
    script_dir = os.path.dirname(os.path.realpath(__file__))
    print script_dir
    try:
        if not args.routes_only:
            cmd_out = subprocess.check_output([script_dir + "/bringup_ccp_csr.sh"] + csrCmdArgs)
            print cmd_out
    except subprocess.CalledProcessError as e:
        print "ERROR creating CSR and DMVPN: {out}".format(out=e.output)
        sys.exit(1)

    LOG.debug("Creating pod network routes")
    create_pod_network_routes(args.vpcNamePrefix, args.onPremPodCidr)
    print "------done ----- "


if __name__ == '__main__':
    main()
