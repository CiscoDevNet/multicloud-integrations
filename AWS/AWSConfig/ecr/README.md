# AWS ECR

Here, 2x solutions for on-premises clusters that wish to use ECR as an image registry are described.

* The first [solution](ecr-registry-creds.md) involves running a long-lived pod that updates docker/ECR tokens for the default ServiceAccount across all Namespaces;

* The second [solution](ecr-cron.md) involves scheduling a CronJob which dynamically updates docker/ECR tokens for a single ServiceAccount in a single Namespace by default;

As described in the [AWS product page](https://aws.amazon.com/ecr/)
"Amazon Elastic Container Registry (ECR) is a fully-managed Docker container registry that makes it easy for developers to store, manage, and deploy Docker container images.... Amazon ECR eliminates the need to operate your own container repositories or worry about scaling the underlying infrastructure. Amazon ECR hosts your images in a highly available and scalable architecture, allowing you to reliably deploy containers for your applications. Integration with AWS Identity and Access Management (IAM) provides resource-level control of each repository..."


Kubernetes offers [native](https://kubernetes.io/docs/concepts/containers/images/#using-aws-ec2-container-registry) ECR support for nodes running on AWS ec2 instances (including EKS worker nodes). In order for this to work, the nodes need to be granted sufficient privileges via an IAM instance profile whereby they are dynamically granted ephemeral credentials via the ec2 metadata (and STS) service.

For EKS clusters, CCP will automatically grant the worker nodes the appropriate ECR read-only privileges via an Instance Profile containing the *AmazonEC2ContainerRegistryReadOnly* AWS Managed Policy:

![](/AWS/images/iam-ecr-policy.png)

Kubernetes clusters hosted on non-AWS infrastructure cannot be assigned IAM instance profiles. Furthermore, unlike e.g. hub.docker.com, ECR does not support the notion of serving 'public' container images. While ECR makes it possible for images to be accessed by other AWS accounts/users/roles, this must be explicitly configured via IAM and requires both an ECR and Docker login step before access to an image/repo is granted. Due to a 12 hour expiry timer on the returned Docker token, this must be repeated every 12 hours. As such, it is currently not possible to access an ECR repo without, at least initially, interacting with IAM.


