
# MultiCloud Integration - AWS

This repository contains engineering notes for the *AWS* MultiCloud integration solution.

* Pre-requisites
  * AWS account with following credentials for the account:
    * AWS Access Key ID
    * AWS Secret Access Key
  * SSH Key Pair configured in the AWS Account
  * System Requirements for CCP Installation can be found [here](https://www.cisco.com/c/en/us/td/docs/net_mgmt/cisco_container_platform/2-2/Installation_Guide/CCP-Installation-Guide-2-2-0/CCP-Installation-Guide-2-2-0_chapter_00.html#id_66020)
  
* [Architecture](./AWSConfig/architecture.md)
  * High Level Diagram and other design documents
  * Common Identity management for on-prem and AWS kubernetes clusters using AWS IAM.
  
* [Configuration of On-prem servers](./OnPremConfig/README.md)
  * Installation and configuration instructions for Cisco ACI, APIC, Hyperflex, ESXi, HX Installer and ASR 1001.  Not all components will be used in every installation.
  
* [Configuration on Public Cloud - AWS](./AWSConfig/README.md)
  * A list of Hybrid Networking solutions Cisco has to offer to connect AWS and on-premise servers.
  * Shared AMI by Cisco - Request access [here](https://www.cisco.com/c/en/us/td/docs/net_mgmt/cisco_container_platform/2-2/User_Guide/CCP-User-Guide-2-2-0/CCP-User-Guide-2-2-0_chapter_01010.html#id_92768)
  * Integration of CCP and EKS
  * Integeration of ECR access through on-prem Kubernetes Clusters.
  
* [Cisco Container Platform](./External/ccp.md) 
  * Instructions to install the Cisco Container Platform and steps to setup a Kubernetes Cluster to get started.
