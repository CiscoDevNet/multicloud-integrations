# Cisco Hybrid integration with AWS

## AWS IAM Common Identity configuration to access on-prem and EKS clusters

CCP can provision EKS and on-premises kubernetes clusters with a common identity schema using the open-source utility 'aws-iam-authenticator'. This utility helps in maintaining a single mode of authentication to manage cluster on EKS as well as on-prem clusters. Details regarding its usage by CCP and a walkthrough of how to extend this to enable common RBAC can be found [here](iam-identity/README.md)

## AWS ECR Access from CCP provisioned on-premises Kubernetes clusters

Two solutions to provide access to Amazon's ECR (Elastic Container Registry) from on-prem clusters can be found [here](/aws/AWSConfig/ecr/README.md)

## Multicloud Networking

A variety of network deployment options that focus on a variety of Hybrid Cloud use cases are described [here](networking/docs/network/README.md).

## EFK Installation on EKS

Instructions to deploy an EFK (ElasticSearch, FluentD, Kibana) stack on EKS can be found [here](efk/README.md)
