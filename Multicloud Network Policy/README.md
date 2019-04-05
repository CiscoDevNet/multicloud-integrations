
# Application of Policy in a Multicloud Environment

The application of policy in a multicloud environment is significantly different than
when policy is applied to a single Kubernetes cluster.  If we consider just policy
at the network level there is a huge difference in effectiveness between the two
enviornments.  Conversley, application level policy has only minor differences
when applied in the two environments.   This content will provide a complete
understanding of network policy application in a multicloud environment. It 
will also provide some contrast between application level policy and network
level policy in a multicloud environment

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
network policy as it applies in a Kubernetes environment
[K8s Network Policy](https://github.com/john-a-joyce/multicloud-integrations/blob/network-policy-struct/Multicloud%20Network%20Policy/k8s_network_polcy.md#network-policy)

Network policy has some significant limitations when applied to multicloud environments.
The limitations we describe in the next section are not simply due to the implementations
that provide the API semantics.  They are more fundimental and would difficult to
overcome at the network layer of the protocol stack.  The limiations are described
here in this next section 
[Limitations](https://github.com/john-a-joyce/multicloud-integrations/blob/network-policy-struct/Multicloud%20Network%20Policy/limitations.md#network-policy-limitations)

We have put together some example scenarios so you can directly see the impact of these limitations
and try things out for yourself.

* [Calico Stars Example Across EKS and CCP with DMVPN](examples/dmvpn_eks_ccp_calico_stars.md)
