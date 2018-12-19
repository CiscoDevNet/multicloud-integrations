
# Solution Overview

Unlike the solution outlined in [ecr-registry-creds.md](ecr-registry-creds.md) which runs a long-lived pod to update the ECR/Docker token across all Namespaces, this solution configures a Kubernetes [CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) to periodically refresh the private registry (Docker) token for ECR in a single Namespace by default.

In doing so, a container (containing the AWS CLI and *kubectl* client) is scheduled to run periodically. The schedule is configured using standard Cron format as specified in this manifest: [cron.yaml](config/cron/cron.yaml)

Example (8-hour schedule):
```
spec:
  schedule: "* */8 * * *"
```

*Should it be desired to create and host a custom version of the container image see [this](container-build/README.md).*

## AWS Account Credentials
AWS account credentials are base64 encoded and configured as an Opaque Kubernetes secret as per [secret.yaml](config/cron/secret.yaml). These AWS credentials are required to authenticate against IAM prior to retrieving a Docker login token.

For security purposes, it may be prudent to use AWS credentials and/or assume an IAM role that is scoped solely to read-only operations against the AWS ECR service. For a suggested IAM policy and method to achieve this, please consult the *AWS Setup* section at the end of this document.

Each parameter (i.e. *AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID, AWS_REGION, AWS_ACCOUNT*) must be encoded as follows. This example shows how to base64 encode the region 'us-west-2':

```
echo -n us-west-2 | base64
dXMtd2VzdC0y
```
These encoded values are then placed in [secret.yaml](config/cron/secret.yaml)

## RBAC Enabled ServiceAccount

To permit the scheduled pod to create and update the ECR/docker secret via the Kubernetes API, a Kubernetes *service account* is configured which is bound to a *Role* containing the following permissions:

```
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: ecr-cred-updater
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "create", "delete"]
- apiGroups: [""]
  resources: ["serviceaccounts"]
  verbs: ["get", "patch"]
```

The service account is specified in *.spec.serviceAccountName* in the CronJob spec:

```
spec:
  serviceAccountName: ecr-cred-updater
```

By default, the Role, RoleBinding and Service Account needed by the pod (launched by the CronJob) to interact with the Kubernetes API are created in the default Namespace. To run in an alternative NS, simply update the metadata statement for each resource in [cron.yaml](config/cron/cron.yaml) and [secrets.yaml](config/cron/secret.yaml) using the following:

```
metadata:
  name: ecr-cred-updater
  namespace: <my-alternative-namespace>
```

# Installing

Once you have updated [secret.yaml](config/cron/secret.yaml) with base64 encoded credentials, perform the following:

1. Create the secret:
```
$ kubectl apply -f config/cron/secret.yaml
```

2. Next, after making any optional changes to [cron.yaml](config/cron/cron.yaml), create the Role, RoleBinding, ServiceAccount and CronJob:
```
$ kubectl apply -f config/cron/cron.yaml
```

## Validation & Troubleshooting

The following commands are scoped to the default Namespace. An alternative Namespace can be specified by appending *-n my-alternative-namespace* to each command below.


Verify the *aws-account_creds* secret has been created:

```
$ kubectl get secrets

NAME                         TYPE                                  DATA   AGE
aws-account-creds            Opaque                                4      3m
...
...
```

Verify the CronJob has been scheduled:

```
$ kubectl get cronjobs.batch

NAME               SCHEDULE      SUSPEND   ACTIVE   LAST SCHEDULE   AGE
ecr-cred-updater   */4 * * * *   False     0        <none>          3m
```

The above output indicates that the CronJob (scheduled every 4x minutes) has been scheduled but has not yet been invoked.

Before the CronJob is executed for the first time, let's take a quick look at the default ServiceAccount. We notice that *imagePullSecrets* is not yet specified in the output:

```
kubectl get sa default -o yaml

apiVersion: v1
kind: ServiceAccount
metadata:
  ...
  ...
```

If we wait another minute and re-run the command, we can see that the CronJob has now executed (note the 'Last Schedule' column):

```
kubectl get cronjobs.batch
NAME               SCHEDULE      SUSPEND   ACTIVE   LAST SCHEDULE   AGE
ecr-cred-updater   * */8 * * *   False     0        1m              4m
```

As a result of this, we should now observe that a Pod has been launched. The execution time for the Pod is quite short, so it's likely it has completed its work and has been terminated:

```
$ kubectl get pods

NAME                                READY   STATUS      RESTARTS   AGE
ecr-cred-updater-1543575120-5jjv5   0/1     Completed   0          2m
```

Nonetheless, if we check the logs for this terminated Pod, we should observe output similar to the following:

```
kubectl logs ecr-cred-updater-1543575360-t2bdd

secret "aws-registry" deleted
secret "aws-registry" created
serviceaccount "default" patched
```

This suggests that the *aws-registry* secret (i.e. our Docker token) has been successfully created. Note: each time the CronJob executes, it deletes & re-creates this secret.

We notice also, from the above output, that the default ServiceAccount has been patched.
If we now take another look at the ServiceAccount, we'll notice that this time *ImagePullSecrets* appears in the output with the name of the newly created *aws-registry* secret:


```
kubectl get sa default -o yaml

apiVersion: v1
imagePullSecrets:
- name: aws-registry
kind: ServiceAccount
  ...
  ...
```

The CronJob is responsible for doing this by virtue of executing this command:

```
kubectl patch serviceaccount default -p '{"imagePullSecrets":[{"name":"aws-registry"}]}'
```

Next, to verify that the *aws-registry* secret has indeed been created and is of the correct type (i.e. *kubernetes.io/dockercfg*), we can run:

```
$ kubectl describe secrets aws-registry

Name:         aws-registry
Namespace:    default
Labels:       <none>
Annotations:  <none>

Type:  kubernetes.io/dockercfg

Data
====
.dockercfg:  4572 bytes
```

Lastly, because the default service account has been patched with an *imagePullSecret* we should now be able to retrieve and run a container image from our private ECR repository **without** explicitly specifying an *imagePullSecret* or *serviceAccount* in the application spec. We'll use our ECR hosted nginx image to verify this. Be sure to update the ECR repo URL in [nginx-deployment.yaml](config/nginx-deployment.yaml) with values specific to your AWS account.

*See [ecr-registry-creds.md](ecr-registry-creds.md) for instructions on how to create a repo and tag an image before uploading to ECR.*

```
$ kubectl apply -f nginx.yaml

deployment.apps/nginx-deployment created
```

We should observe that 2x nginx Pods have been successfully launched:

```
kubectl get pods

NAME                                READY   STATUS      RESTARTS   AGE
ecr-cred-updater-1543577520-nvczx   0/1     Completed   0          1m
nginx-deployment-6588884f9b-ft6bs   1/1     Running     0          8s
nginx-deployment-6588884f9b-m68m8   1/1     Running     0          8s
```

If we check the events for one of the newly launched pods, we should observe that the image pull from ECR has been successful:

```
$ kubectl describe pod nginx-deployment-6588884f9b-ft6bs

...
...
Containers:
  nginx:
    Container ID:   docker://66b7c5911c026956fad8b62964964e189fecf5586e09f232ddbea3de17d1bc01
    Image:          1234567890.dkr.ecr.us-west-2.amazonaws.com/ccp-repo/nginx
    Image ID:       docker-pullable://1234567890.dkr.ecr.us-west-2.amazonaws.com/ccp-repo/nginx@sha256:d98b66402922eccdbee49ef093edb2d2c5001637bd291ae0a8cd21bb4c36bebe

    ...
    ...

Events:
  Type    Reason     Age   From                                         Message
  ----    ------     ----  ----                                         -------
  Normal  Scheduled  33s   default-scheduler                            Successfully assigned default/nginx-deployment-6588884f9b-ft6bs to ob-ecr-validation-workere5f9773e38
  Normal  Pulling    32s   kubelet, ob-ecr-validation-workere5f9773e38  pulling image "1234567890.dkr.ecr.us-west-2.amazonaws.com/ccp-repo/nginx"
  Normal  Pulled     32s   kubelet, ob-ecr-validation-workere5f9773e38  Successfully pulled image "1234567890.dkr.ecr.us-west-2.amazonaws.com/ccp-repo/nginx"
  Normal  Created    32s   kubelet, ob-ecr-validation-workere5f9773e38  Created container
  Normal  Started    31s   kubelet, ob-ecr-validation-workere5f9773e38  Started container
  ```

This has been achievable because all new pods launched in the Namespace will have the following (dynamically) added to their spec:

```
spec:
  imagePullSecrets:
    - name: aws-registry
```

which can be inspected by running the following command:

```
kubectl get pod <pod-name> -o yaml
```


# Limitations
1. The first invocation of the CronJob will only occur as soon as the interval specified lapses (e.g. in 8 hours). If this time interval is too long, then the shell commands contained in [cron.yaml](config/cron/cron.yaml) could be executed.

2. By default, this solution works for a single namespace (*default* unless otherwise specified). To implement this solution, 'as-is', for additional namespaces requires that the CronJob and secret are created/invoked in those additional namespaces.


# AWS Setup
**User/Policy Creation**

Here is one method to create scoped read-only access to ECR for a local IAM user. An alternative would be to create an IAM role with a policy identical to the one outlined below.

Let's create a local IAM user with read-only ECR permissions and nothing else. We'll call this user 'ccp-ecr-user'.

```
aws iam create-user --user-name ccp-ecr-user

{
    "User": {
        "Path": "/",
        "UserName": "ccp-ecr-user",
        "UserId": "AIDAIUNERHWQL3CE73NIK",
        "Arn": "arn:aws:iam::<AWS_ACCOUNT_ID>:user/ccp-ecr-user2",
        "CreateDate": "2018-10-22T14:02:54Z"
    }
}

```
Next, we create some API credentials which we'll need later:

```
aws iam create-access-key --user-name ccp-ecr-user

{
    "AccessKey": {
        "UserName": "ccp-ecr-user",
        "AccessKeyId": "REDACTED",
        "Status": "Active",
        "SecretAccessKey": "REDACTED",
        "CreateDate": "2018-10-22T14:12:33Z"
    }
}
```

And now, we grant ECR readonly permissions by attaching an AWS managed policy to our newly created user:

```
aws iam attach-user-policy --user-name ccp-ecr-user --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
```

which, under-the-hood, will grant the following IAM policy to the user. This equates to read-only access to ECR.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:GetRepositoryPolicy",
                "ecr:DescribeRepositories",
                "ecr:ListImages",
                "ecr:DescribeImages",
                "ecr:BatchGetImage"
            ],
            "Resource": "*"
        }
    ]
}
```
