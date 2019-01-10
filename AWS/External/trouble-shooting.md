# Trouble Shooting Guide - Alchemy Solution

The following guide addresses some of the questions or troubles that may occur during the usage of the CCP's Alchemy features.

## Installation of CCP Control Plane



## AWS IAM Authentication

1. Do I need separate credentials for managing the on-prem cluster?
   
   If you have enabled the `AWS IAM Authentication` switch on during the on-prem cluster creation, then you can use the AWS credentials to manage on-prem kubernetes cluster.

2. I forgot to turn on the switch for `AWS IAM Authentication` during the cluster creation. What should I do?


## On-prem Cluster

1. I tried Upgrading my on-prem cluster, but it failed to upgrade. Will the cluster roll-back to previous version?
   
   Yes.

2. I am unable to reach to the on-prem Kubernetes Cluster through `kubectl`. What are the steps to connect?
    1. Normal Operations:
    2. After the Upgrade of the Cluster is successfully completed.
    3. The Upgrade process failed and rolled back to previous versions.
3. During the upgrade process of the Kubernetes, is the cluster available for normal operations and functions? What is the strategy used during the Upgrade process?
4. Does Upgrade process of on-prem clusters means upgrade of the Master nodes as well as Worker Nodes?

## AWS EKS Cluster

1. Should I create any special Policies or Roles before Cluster creations on EKS?
2. Can I SSH into my EKS worker nodes viz. EC2 Instances?

   No. You cannot login directly. To access the worker nodes you will have to create Bastion Host which has permissions to ssh into the worker nodes.

3. Can I access or SSH into EKS Master nodes?
   
   By default Amazon EKS doesn't provide access to EKS Master nodes. The EKS Master nodes are managed by AWS. The Master Nodes are hidden from the customer and not accessible through any API's or `kubectl`. 

4. Is it possible to use my personal AMI (Amazon Machine Images) to provision as EKS worker nodes? 

    No. Currently on Cisco Shared AMI are supported.

<!--5. Can I upgrade/change my EKS Worker nodes? How can I do that? What is the strategy used in upgrading the same?
   
6. I deleted an EKS cluster from the CCP UI, but the entry for the cluster is stuck at some status. When I checked AWS EKS Console, the EKS cluster and related resources were deleted. What should I do to remove the entry from the CCP UI ?
-->

## Log Generation

1. The support team has asked me to attach logs from the on-prem Master Nodes. How can I get those logs?

    SSH into the on-prem Kubernetes Master node. The Public IP address of the master node can be obtained from the CCP UI. Execute the following commad to generate a package of logs to submit to support team.

    ```shell
    $ sudo sosreport
    ```
    This will generate a `tar.xz` compressed file in the /tmp directory.

2. How do I get logs from the AWS EKS cluster ?

    AWS EKS provides with inbuilt support to gather the EKS logs to be accessed through CloudTrail. More details on this can be obtained from AWS Documentation [here](https://docs.aws.amazon.com/eks/latest/userguide/logging-using-cloudtrail.html). 
