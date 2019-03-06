
# Create CCP AWS cluster and link to on-prem via CSR & DMVPN

## bringup_aws_cluster.py

Example:

```
$ cat tim_aws.yaml
---
name: taws4
subnet:
  cidr: 10.0.0.0/16
  publicCidrs:
    - 10.0.106.0/24
    - 10.0.107.0/24
    - 10.0.108.0/24
  privateCidrs:
    - 10.0.109.0/24
    - 10.0.110.0/24
    - 10.0.111.0/24

role_arn_name: k8s-ccp-user

ssh_keys:
  - tim-key

$ bringup_aws_cluster.py --ccpIp 127.0.0.1 --ccpPort 29443 --ccpPassword 'abcdefg' --providerStr tim --clusterCfgFile tim_aws.yaml

```

## bringup_csr.py

Example:

```
$ cat dmvpn_conf.yaml
---
InstanceType: c4.large
InboundSSH: 0.0.0.0/0
ike_keyring_peer:
  ip_range:
    start: 0.0.0.0
    end: 0.0.0.0
  pre-shared-key: abcdefghijklmn012345

ike_profile:
  remote_peer_ip:  <public/routeable IP of the remote peer>

DmvpnIp: 10.250.0.9
DmvpnNetmask:  255.255.255.0

nhrp:
  key:          keykey00
  HubTunnelIP:  10.250.0.1

ospf:
  processId: 10
  authKey: DEADBEEF0123456789
  tunnelNetwork: 10.250.0.0
  tunnelWildcard: 0.0.0.255
  vpcArea: 2
  tunnelArea: 0


$ bringup_csr.py --vpcNamePrefix taws4 --sshKey tim-key --onPremCidr 10.1.0.0/16 --onPremPodCidr 192.168.0.0/16 --clusterCfgFile tim_aws.yaml --dmvpnCfgFile dmvpn_conf.yaml --debug

```

# aws-get-vpc-info.sh

The script is used to gather the route table IDs and private subnet CIDRs after the CCP automation has created all of the relevant VPC resources.

```
Example use of the script:
./aws-get-vpc-info.sh vpc-043953bf3fd40447c
 The VPC ID BEING USED IS
vpc-043953bf3fd40447c
 GET ROUTE TABLE IDs
 Private route table 1 ID is:
rtb-0b5ed35d499184e53
 Private route table 2 ID is:
rtb-06f537ceb7ec49160
 Private route table 3 ID is:
rtb-02f09cafd1f7db0b5
 GET ALL SUBNET CIDR RANGES
 Private subnet 1 CIDR range is:
172.16.3.0/24
 Private subnet 2 CIDR range is:
172.16.4.0/24
 Private subnet 3 CIDR range is:
172.16.5.0/24
```
