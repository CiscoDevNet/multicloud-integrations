
# Using Policy in a Multicloud Environment

The ability to use policy in a multicloud environment is significantly different than
when policy is used in a single Kubernetes cluster.  If we consider just policy
at the network level there is a huge difference in effectiveness between the two
environments.  Conversley, application level policy has only minor differences
when used in the two environments.  This content will provide a complete
understanding of network policy usage in a multicloud environment. It 
will also provide some contrast between application level policy and network
level policy in a multicloud environment.  It is best to read this content by
following the links as they occur in this README.

Topics covered:

* A short introduction to network policy and some of the different variants

* Discussion of the networking aspects that affect network policy behavior and capabilities

* A contrast of network policy capabilities in a single cloud environment versus a multicloud environment

* Enumeration of additional work or functionality that could be added to improve the behavior

* Differences in behavior based on the environment hosting the Kubernetes cluster

* A contrast between application level policy and network level policy

The term "policy" is an overloaded term which has different meanings based on the context it
is used.  When readers see the word "policy" their first thoughts are often different based on
the individuals background.  Therefore to start us off we will first describe what we mean by
network policy as it applies in a Kubernetes environment.  Please follow link to the more
detailed discussion of network policy. 

# [K8s Network Policy](https://github.com/john-a-joyce/multicloud-integrations/blob/network-policy-struct/Multicloud%20Network%20Policy/k8s_network_polcy.md#network-policy)

Network policy has some significant limitations when applied to multicloud environments.
The limitations we describe in the next section are not simply due to the implementations
that provide the API semantics.  They are more fundimental and would difficult to
overcome at the network layer of the protocol stack.  Please follow the link to the more
detailed discussion of these limitations.

# [Limitations](https://github.com/john-a-joyce/multicloud-integrations/blob/network-policy-struct/Multicloud%20Network%20Policy/limitations.md#network-policy-limitations)

We have put together some example scenarios so you can directly see the impact of these limitations
and try things out for yourself.  Please follow the next link to follow the procedure or you can jump right to specfic steps if your environment is already partially setup.

# [Calico Stars Example Across EKS and CCP with DMVPN](examples/dmvpn_eks_ccp_calico_stars.md)

## [Deploying the Multicloud Clusters and DMVPN Connectivity](examples/dmvpn_eks_ccp_calico_stars.md#deploying-the-multicloud-clusters-and-dmvpn-connectivity)

## [Deploy the AWS EKS Cluster](examples/dmvpn_eks_ccp_calico_stars.md#deploy-the-aws-eks-cluster)

## [Deploy the DMVPN & Inter-cloud Pod Routing Connectivity](examples/dmvpn_eks_ccp_calico_stars.md#deploy-the-dmvpn--inter-cloud-pod-routing-connectivity)

## [Deploying the Calico Stars Application Across Clouds](examples/dmvpn_eks_ccp_calico_stars.md#deploying-the-calico-stars-application-across-clouds)
