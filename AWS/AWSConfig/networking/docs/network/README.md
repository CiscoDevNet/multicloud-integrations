## Cisco and Amazon Web Services Network Documentation

This landing page is for the Cisco and Amazon Web Services (AWS) network documentation. The network deployment options referenced below are in support of the joint Cisco and AWS program that focuses on a variety of Hybrid Cloud use cases.  The primary use case leverages the [Cisco Container Platform](https://www.cisco.com/c/en/us/products/cloud-systems-management/container-platform/index.html) and its automated deployment of an Enterprise on-premises [Kubernetes](https://kubernetes.io/) cluster, an automated deployment of an [Elastic Container Service for Kubernetes Service (EKS)](https://aws.amazon.com/eks/) cluster and an [Elastic Container Registry (ECR)](https://aws.amazon.com/ecr/) repository at [Amazon Web Services (AWS)](https://aws.amazon.com/).

The following network deployment options support the primary use case mentioned above by providing various topology choices for connecting Cisco Container Platform workloads that exist at an Enterprise site to Amazon EKS workloads.

* [Internet Over-the-Top (OTT) Network Deployment](ott/README.md)
* [DMVPN-based Network Deployment using an AWS-hosted Cisco CSR 1000v (single router model - FOR PoC ONLY)](csr-dmvpn/README.md)

### Kubernetes Pod Networking

For hybrid-cloud workloads interconnected via VPN, it is possible to route between Kubernetes pods located on either side of the VPN tunnel.  The following sections provide details on setups and considerations:

*  [Enabling Hybrid Cloud Pod Networking for the AWS CSR-DMVPN Model](csr-dmvpn/pod-networking.md)
*  [Setting up K8s Multicluster Services in NAT-less hybrid cloud setups](/common/networking/multicluster_services.md)
