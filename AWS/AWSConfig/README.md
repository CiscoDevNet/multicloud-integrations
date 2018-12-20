# AWS Integration

## AWS IAM Common Identity

CCP can provision EKS and on-premises clusters with a common identity schema using the open-source utility 'aws-iam-authenticator'. Details regarding its usage by CCP and a walkthrough of how to extend this to enable common RBAC can be found [here](iam-identity/README.md)


## AWS ECR Access from CCP On-premises Kubernetes Clusters

Two solutions to provide access to Amazon's ECR (Elastic Container Registry) from on-prem clusters can be found [here](/aws/AWSConfig/ecr/README.md)

## MultiCloud Networking
A variety of network deployment options that focus on a variety of Hybrid Cloud use cases are described [here](networking/docs/network/README.md).

## EFK Installation on EKS 
Instructions to deploy an EFK (ElasticSearch, FluentD, Kibana) stack on EKS can be found [here](efk/README.md)
