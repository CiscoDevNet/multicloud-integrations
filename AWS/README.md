
# Cisco hybrid integration with AWS

This repository contains engineering documentation covering components of the **Cisco Hybrid Solution for Kubernetes on AWS**.

Topics covered:

* Integration between the Cisco Container Platform (CCP) and AWS’s Elastic Container Service for Kubernetes (EKS), leveraging AWS’s Identity And Access Management (IAM)

* Access to AWS’s Elastic Container Registry (ECR)
  
* Networking deployment options
  
* Deployment instructions for EKF (ElasticSearch, FluentD, Kibana)


Note: The remaining components of the solution (AppDynamics, Cisco Stealthwatch Cloud, Cisco CloudCenter, Cisco HyperFlex/Cisco UCS and Cisco Nexus) are not covered in this documentation

![cisco-hybrid-aws](/aws/images/cisco-hybrid-aws.png)


* Pre-requisites
  * AWS account with following credentials for the account:
    * AWS Access Key ID
    * AWS Secret Access Key
  * SSH Key Pair configured in the AWS Account
  * System Requirements for CCP Installation can be found [here](https://www.cisco.com/c/en/us/td/docs/net_mgmt/cisco_container_platform/2-2/Installation_Guide/CCP-Installation-Guide-2-2-0/CCP-Installation-Guide-2-2-0_chapter_00.html#id_66020)
  
* [Architecture](./AWSConfig/architecture.md)
  * High Level Diagram and other design documents
  
* [Configuration on Public Cloud - AWS](./AWSConfig/README.md)
  * AWS IAM Common Identity configuration to access on-prem and EKS clusters.
  * Integeration of ECR access through on-prem Kubernetes Clusters.
  * A list of Hybrid Networking solutions Cisco has to offer to connect AWS and on-premise servers.
  * EFK Installation on EKS.
  * Shared AMI by Cisco - Request access [here](https://www.cisco.com/c/en/us/td/docs/net_mgmt/cisco_container_platform/2-2/User_Guide/CCP-User-Guide-2-2-0/CCP-User-Guide-2-2-0_chapter_01010.html#id_92768)
  
* [Cisco Container Platform](./External/ccp.md) 
  * Instructions to install the Cisco Container Platform and steps to setup a Kubernetes Cluster to get started.
