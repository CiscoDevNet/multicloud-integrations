# High Level Diagram

![](/aws/images/Solution_Architecture.png)

From the above diagram, CCP can be used to provision Kubernetes clusters on on-premises virtualized infrastructure (VMware, today) and on AWS using EKS. CCP provides the option of deploying AWS IAM authentication plugin on on-premise clusters which allows the AWS registered users to access the Kubernetes cluster using the AWS IAM credentials.

# AWS - IAM authentication integration

The AWS IAM credentials are used to authenticate to the Kubernetes cluster. To enable this, the solution uses `aws-iam-authenticator` utilty to which helps in maintaining a single mode of authentication to manage the on-prem Kubernetes cluster as well as the AWS EKS Cluster. More details on the implementation can be found [here](/aws/AWSConfig/README.md).
