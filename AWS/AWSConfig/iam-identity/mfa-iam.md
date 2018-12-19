# MFA enabled IAM ROLES

IAM Roles that contain a condition in their trust policy to enforce the use of MFA/2FA can be used with *aws-iam-authenticator*. However, there are two important caveats to be aware of.


Firstly, here's an example IAM Role trust policy which enforces the use of MFA:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::1234567890:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
```

It is possible to augment this trust policy with a statement similar to the following to reduce the frequency of inputting new MFA codes to 60mins.

```
"Condition": {
        "NumericLessThan": {
          "aws:MultiFactorAuthAge": "3600"
        }
      }
```

**However, aws-iam-authenticator running on the master node(s), makes an API call to the STS (secure token service) via a pre-signed URL which is stamped with a validity period of 15minutes**

## Caveat #1
By default, *aws-iam-authenticator* will **always** prompt for an MFA code each time a kubectl command is run. Specifying a *MultiFactorAuthAge* in the role's trust policy will have no effect. [This PR](https://github.com/kubernetes-sigs/aws-iam-authenticator/pull/140) will add cache functionality for tokens used during the auth process when it is merged.

## Caveat #2
The typical pattern for specifying an IAM role in *kubeconfig* for use by *aws-iam-authenticator* is as follows:

```
users:
- name: kubernetes-admin
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "my-k8s-cluster"
        - "-r"
        - "arn:aws:iam::1234567890:role/iam-role-to-assume"
```

For MFA enabled IAM roles the above pattern won't work. A workaround is to create a named AWS profile (*~/.aws/config*) e.g:

```
[profile with-mfa]
role_arn=arn:aws:iam::1234567890:role/iam-role-with-mfa
source_profile=default
mfa_serial = arn:aws:iam::1234567890:mfa/my-username
```

Where the credentials to use when assuming the above role are contained in: *~/.aws/credentials*:

```
[default]
aws_access_key_id = keyswithpermissiontoassumeiamrole
aws_secret_access_key = keyswithpermissiontoassumeiamrole
```

and then specify this using the *AWS_PROFILE* environment variable or declare it in *kubeconfig* as follows:

```
users:
- name: kubernetes-admin
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      command: aws-iam-authenticator
      args:
        - "token"
        - "-i"
        - "my-k8s-cluster"
      env:
      - name: "AWS_PROFILE"
        value: "with-mfa"
```

Now, if we execute a *kubectl* command we will be prompted to enter a token before authentication succeeds:

```
$ kubectl get nodes --kubeconfig ~/.kube/config-mfa
Assume Role MFA token code: 123456

NAME                           STATUS   ROLES    AGE   VERSION
my-k8s-cluster-master764da57704   Ready    master   1d    v1.11.3
my-k8s-cluster-worker40f640b60d   Ready    <none>   1d    v1.11.3
my-k8s-cluster-worker4690ea0c0f   Ready    <none>   1d    v1.11.3
```
