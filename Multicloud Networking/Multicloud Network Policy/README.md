
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

## [K8s Network Policy](./k8s_network_policy.md#network-policy)

Network policy has some significant limitations when applied to multicloud environments.
The limitations we describe in the next section are not simply due to the implementations
that provide the application program interface (API) semantics.  They are more
fundimental and would difficult to overcome at the network layer of the protocol
stack.  Please follow the link to the more detailed discussion of these limitations.

## [Limitations](./limitations.md#network-policy-limitations)

We have put together some example scenarios so you can directly see the impact of these limitations
and try things out for yourself.  Please follow the next link to follow the procedure or you can jump right to specfic steps if your environment is already partially setup.

## [Calico Stars Example Across EKS and CCP with DMVPN](../Multicloud%20Automation/examples/dmvpn_eks_ccp_calico_stars.md)

* [Deploying the Multicloud Clusters and DMVPN Connectivity](../Multicloud%20Automation/examples/dmvpn_eks_ccp_calico_stars.md#deploying-the-multicloud-clusters-and-dmvpn-connectivity)

* [Deploy the AWS EKS Cluster](../Multicloud%20Automation/examples/dmvpn_eks_ccp_calico_stars.md#deploy-the-aws-eks-cluster)

* [Deploy the DMVPN & Inter-cloud Pod Routing Connectivity](../Multicloud%20Automation/examples/dmvpn_eks_ccp_calico_stars.md#deploy-the-dmvpn--inter-cloud-pod-routing-connectivity)

* [Deploying the Calico Stars Application Across Clouds](../Multicloud%20Automation/examples/dmvpn_eks_ccp_calico_stars.md#deploying-the-calico-stars-application-across-clouds)

## Application Level Policy

The previous discuss focused on network level policy.  We will move on to
applicaiton level policy or more precisely policy that can be applied at layer 7
of the protocol stack. Application layer policy is much more suitable to a
multicloud environment. There are a few reasons for this. One of the primary
reasons is that the policy can be expressed in more or less the same language
as the application itself as it is deployed across multiple clusters.  Therefore,
it doesn't rely on being expressed in terms of network addressing constructs
that are not consistent across multiple clouds.  Please follow the link for a more 
complete discussion of the additional benefits.

## [Application Policy Advantages](./app_policy.md##application-level-policy)
