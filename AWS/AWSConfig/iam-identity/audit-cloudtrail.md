# Identifying User Authentication based on IAM SessionName

    Note: EKS does not provide access to the master nodes on which the aws-iam-authenticator pod(s) have been deployed. Therefore, it is not currently possible to view the logs for the aws-iam-authenticator pod on an EKS cluster. This solution currently only works for on-premises Kubernetes clusters.

Consider the following configMap snippet, where {{SessionName}} has been specified:



 ```- roleARN: arn:aws:iam::1234567890:role/k8s-admin-role
        username: kubernetes-admin:{{SessionName}}
        groups:
        - system:masters
```

Let's assume we have a local iam user called '*k8s-admin-user*' who needs to assume the role: '*arn:aws:iam::1234567890:role/k8s-admin-role*' in order to authenticate to a Kubernetes cluster. 
        
    Note: there could potentially be many people assuming the same role to authenticate!

Each time a user executes a kubectl command, a log similar to the following will be produced (in the aws-iam-authenticator pod):

```
kubectl logs -f aws-iam-authenticator-xxxx -n kube-system
```

```
time="2018-12-20T11:17:50Z" level=info msg="access granted" arn="arn:aws:iam::1234567890:role/k8s-admin-role" client="127.0.0.1:42858" groups="[system:masters]" method=POST path=/authenticate uid="heptio-authenticator-aws:1234567890:ABCDEFGHIJKLMNOPQRSTU" username="kubernetes-admin:1545304668958751972"
```

Note from the log above how *{{SessionName}}* has been interpolated to *'1545304668958751972'*

The log above tells us the Role ARN that was used to authenticate, but doesn't tell us what *individual* assumed the role.

To determine that, we can consult the AWS CloudTrail logs 

        Note: there can be a ~15min delay before the entry appears in CloudTrail).

If we search our CloudTrail logs for '*1545304668958751972*' we should find an event similar to the following:

```{
    "eventVersion": "1.05",
    "userIdentity": {
        "type": "IAMUser",
        "principalId": "AIDAIV3YI4IAHEX26LLYW",
        "arn": "arn:aws:iam::1234567890:user/k8s-admin-user",
        "accountId": "1234567890",
        "accessKeyId": "ABCDEFGHIJKLMNOPQ",
        "userName": "k8s-admin-user"
    },
    "eventTime": "2018-12-20T11:17:49Z",
    "eventSource": "sts.amazonaws.com",
    "eventName": "AssumeRole",
    "awsRegion": "us-east-1",
    "sourceIPAddress": "IP.IP.IP.IP",
    "userAgent": "aws-sdk-go/1.12.8 (go1.10.1; darwin; amd64)",
    "requestParameters": {
        "roleArn": "arn:aws:iam::1234567890:role/k8s-admin-role",
        "roleSessionName": "1545304668958751972",
        "durationSeconds": 900
    },

<snipped for brevity>
```

We can see from the CloudTrail log above that roleSessionName '*1545304668958751972*' corresponds to the value for *{{SessionName}}* we've seen in the *aws-iam-authenticator* pod logs, but more importantly we can see this:

```
"userName": "k8s-admin-user"
```

And now we know that the individual user who used the IAM role to authenticate to the k8s cluster is a user called '*k8s-admin-user*'.