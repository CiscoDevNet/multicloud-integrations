# High Level Diagram

![](/aws/images/Solution_Architecture.png)

From the above diagram, CCP can be used to provision kubernetes clusters on on-premises and AWS EKS. CCP allows deploying AWS IAM authentication plugin on on-premise clusters which allows the AWS registered users to access kubernetes cluster using the AWS IAM credentials.

# AWS - IAM authentication integration

The AWS IAM credentials are used to authenticate to the kubernetes cluster. To enable this, the solution uses `aws-iam-authenticator` utilty to which helps in maintaining a single mode of authentication to manage the on-prem kubernetes cluster as well as the AWS EKS Cluster. More details on the implementation can be found [here](/aws/AWSConfig/README.md).