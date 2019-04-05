# Multicloud Network Policy Example: Calico Stars App on EKS and CCP Tenant Clusters

In this example we use the "Stars" example application created by the Calico project to
demonstrate the effects of Kubernetes network policies.  This example has a nice simple
UI that illustrates communication between microservices.  To demonstrate multicloud
network policy, we show a deployment with microservices in different clouds and example
Kubernetes network policy configurations to achieve the same behavior as the single
cluster original demo.  The example is built upon the multicloud routing capabilities
in a multicloud DMVPN design.

This example goes through expansion of the CCP tenancy into the AWS cloud via the CCP
integrated EKS deployment capability.  Additionally, the example highlights the
multicloud DMVPN connectivity possibilities via use of example automation for provisioning
an AWS EC2 hosted CSR instance as a DMVPN endpoint in the VPC and distributing routes to
on-premises Kubernetes tenant pods into the VPC routing infrastructure.

## Prerequisites

1. CCP installation with a local tenant Kubernetes cluster deployed.
1. CCP configured with an AWS "infrastructure provider" tied to an AWS IAM role with
   sufficient privileges to create an EKS cluster.
1. For executing the scripts in this example shell environment variable `MCINTEG_ROOT`
   must be set to the root directory of the locally cloned `multicloud-integrations` repo.

## Deploying the Multicloud Clusters and DMVPN Connectivity

### Deploy the AWS EKS Cluster

### Deploy the DMVPN & Inter-cloud Pod Routing Connectivity

## Deploying the Calico Stars Application Across Clouds

In this example, we deploy 2 services in the on-premises CCP tenant cluster and 2 services
in the EKS cluster.

**Figure 1.** Services `frontend` and `backend` on-premises; service `client` and `management-ui` in EKS

![multicluster_stars_deployment.png](images/multicluster_stars_deployment.png)

### Deployment of Services

```
# NOTE: kubectl context "ccp_mc1" is the on-premises k8s cluster
#       context "aws" is the EKS k8s cluster with DMVPN connectivity to on-prem

kubectl apply -f namespace.yaml --context ccp_mc1
kubectl apply -f backend.yaml --context ccp_mc1
kubectl apply -f frontend.yaml --context ccp_mc1

kubectl create ns management-ui --context aws
kubectl create ns client --context aws
kubectl apply -f management-ui.yaml --context aws
kubectl apply -f client.yaml --context aws
```

### Mapping Services into Each Cluster's DNS

```
$ cat <<EOF > ~/tmp/multicluster_stars_svcs.yaml
clusters:
- name: onPremCluster1
  kubeconfig: /cfg/kubeconfig-onPremCluster1.yaml
  services:
  - namespace: stars
- name: eksCluster1
  kubeconfig: /cfg/kubeconfig-eksCluster1.yaml
  services:
  - namespace: management-ui
  - namespace: client
EOF

$ $MCINTEG_ROOT/create_svc_endpoints.py --clusterSvcCfgFile ~/tmp/multicluster_stars_svcs.yaml --debug
```


### Accessing the UI

Get the external service address for the `stars` UI as follows:

```
kubectl get svc -n management-ui -o wide
```

When accessing the UI with no network-policies applied the following should be displayed:

![calico-stars-default.png](images/calico-stars-default.png)

### Applying Network Policy

**TODO**  cleanup/explain the policy apply stuff

```
# Apply default-deny policy to client (EKS) and stars (on-prem) namespaces
cat <<EOF > ~/tmp/default-deny.yaml
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  name: default-deny
spec:
  podSelector:
    matchLabels: {}
EOF

kubectl apply -n stars --context ccp_mc1 -f ~/tmp/default-deny.yaml
kubectl apply -n client --context aws -f ~/tmp/default-deny.yaml

# Apply the normal backend policy to on-prem
cat <<EOF | kubectl apply --context ccp_mc1 -f -
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  namespace: stars
  name: backend-policy
spec:
  podSelector:
    matchLabels:
      role: backend
  ingress:
    - from:
      - podSelector:
            matchLabels:
              role: frontend
      ports:
        - protocol: TCP
          port: 6379
EOF

# Apply the normal allow-ui-client in EKS
cat <<EOF | kubectl apply --context aws -f -
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  namespace: client 
  name: allow-ui 
spec:
  podSelector:
    matchLabels: {}
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              role: management-ui 
EOF


# Allow-ui in on-prem stars namespace
mgmtui_ep=$(kubectl get endpoints management-ui -n management-ui --context aws -o jsonpath="{.subsets[0].addresses[0].ip}")
mgmtui_ep_port=$(kubectl get endpoints management-ui -n management-ui --context aws -o jsonpath="{.subsets[0].ports[0].port}")

cat <<EOF | kubectl create --context ccp_mc1 -f -
apiVersion: extensions/v1beta1
kind: NetworkPolicy
metadata:
  name: allow-ui
  namespace: stars
spec:
  ingress:
  - from:
    - ipBlock:
        cidr: ${mgmtui_ep}/32
  policyTypes:
  - Ingress
EOF

# Allow client (EKS) to access frontend (on-prem)
client_ep=$(kubectl get endpoints client -n client --context aws -o jsonpath="{.subsets[0].addresses[0].ip}")
cat <<EOF | kubectl create --context ccp_mc1 -f -
kind: NetworkPolicy
apiVersion: networking.k8s.io/v1
metadata:
  namespace: stars
  name: frontend-policy
spec:
  podSelector:
    matchLabels:
      role: frontend
  ingress:
    - from:
        - ipBlock:
            cidr: ${client_ep}/32
      ports:
        - protocol: TCP
          port: 80
EOF
```

Upon completion the desired application communication of UI as a allowed client to all services, C allowed client to F, and F allowed client to B should be shown as in the image below:

![stars-final.png](images/stars-final.png)

## References

- [Enabling Hybrid Cloud Pod Networking for the AWS CSR-DMVPN Model](../../AWS/AWSConfig/networking/docs/network/csr-dmvpn/pod-networking.md)

- [K8s Multicluster Services in NAT-less Hybrid Cloud](../../common/networking/multicluster_services.md)

- [Calico Stars Demo on AWS](https://docs.aws.amazon.com/eks/latest/userguide/calico.html)