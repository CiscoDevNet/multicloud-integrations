# Network Policy Limitations

In our testing we have found network policy works well in a single cloud environment
in every environment we tested.  When we have extended that testing to multicloud
environments we found significant limitations.  If the multicloud environment
features a Virtual Private Network (VPN) without Network Address Translation (NAT)
between the inter-cloud pod traffic then network policy has some limited utility.
If any sort of NAT is used between the inter-cloud pod traffic then network
policy becomes almost useless.  When network policy is applied in a multicloud
environment but the traffic is between pods in the same cluster things work
as well as in a single cloud environment.  In other words the limitations that
will be described below only affect inter-cloud traffic.

# Application Policy

Application level policy refers to the ability to define policy at Layer 7 of the protocol
stack.  There are many solutions that offer application level policy including:
[Istio](https://istio.io/)
[Calico](https://docs.projectcalico.org/v3.6/security/app-layer-policy/)
[Cilium](https://cilium.io/)
[Linkerd](https://linkerd.io/)

Application policy offers a much higher level of functionality than the network policy options
discussed in this blog.  Unlike network policy, application level policy retains its benefits
even in multicloud environments regardless of whether NAT is in use or not. Later sections
will explain why and discuss application layer policy in more detail.

# Review of Match Criteria For Intra-cloud Network Policy

Distilling the Calico and K8s network policy APIs the user can specify matches against
pods, namespaces, labels (i.e. all network endpoints in given namespace) and
Internet Protocol (IP) Classless Inter-domain Routing (CIDR)s.  The IP CIDRs
matches transcend all K8s resource types.  For example the CIDR matches will work for pod
IPs, cluster IPs, load balance IPs or external IPs that fall within the CIDR. The matches
can be applied in the ingress, egress or both directions.  The APIs also allow matching based on
specific protocols.  For traffic between two endpoints in the same cluster (i.e. Intra-cloud) 
then this match criteria can be directly translated to specific IP and port matches in the datapath.

# Inter-cloud Match Limitations

The inter-cloud use case limitations are due to the following factors

* All of the network policy solutions are only able to use state from the local cluster to
translate name based references to the layer 3 addresses. The rules that are installed in the
dataplane are always IP CIDR based. Therefore matches based on pod name, labels or namespaces
won't find IP CIDRs from any remote clouds.

* In Kubernetes, pods may be very dynamic and come and go on relatively short time scales.
The pod IPs will change during this churn. Therefore it is impractical without special
synchronization code to refer to pods on remote clouds based on their IP address.

* When NAT is used between the clouds the individual IPs within the cloud are obscured by the
NAT addresses.  So references to remote clouds pod traffic can only be done using the
source IPs assigned to the NAT pool (for ingress rules) or publically exposed service
IPs (for egress rules)

* Even when NAT is not specifically configured between the clouds some public clouds
default behavior is to use Source NAT (SNAT) when leaving the cluster (e.g. AWS)

* Some network policy implementations will only pay attention to the address in the
endpoint spec. Calico is one example.  So name based references that should match
against a headless service won't be translated into dataplane rules for the IP
address the headless service is pointing to.

Considering the above limitations what is practical in both NAT and Non-NAT environments to restrict inter-cloud traffic?

## Non-NAT environments

For environments that don't include any type of NAT the inter-cloud traffic cannot be
restricted using name based (pod name, namespace, label) references.  Therefore IP
CIDR based rules must be used.  To be of any practical use the rules must be expressed
at a very granular level.  For most deployments this would require that individual pod
IPs be used in the API calls.  As a contrived example let's say Cloud 1 has both
user interface and front-end pods while cloud 2 hosts back-end pods.  The desired policy
is that the back-end should only accept requests from the front-end and no other clients.
In such an example the policy rules would need to be granular enough to delineate between
the front-end and UI pods from the same cluster. Without specialized pod IP Address Management (IPAM) individual pod IP must be used.

Even when the rules are expressed at the level of individual pod IPs the pod IPs are likely to
change over time unless it is an extremely stable environment. If the pod IPs can change then
for this to be practical some automated way to update the rules on a specific cloud as the
IPs on remote clouds change is required.

Another rule that might be useful in some multicloud environments is client side checks
(i.e. egress rules) that should prevent specific clients from accessing public facing
service IPs (i.e. loadbalance IPs). Expressing the rule via the API is usually
straight forward as those loadbalance IPs are unlikely to change over time.

## NAT environments

When the multi-cloud environment includes NAT there are very few ways to use network policy
to restrict inter-cloud communication in a meaningful way. This is because the pod IPs also
are not practical to use.  Instead only the NAT gateway IPs can be used to refer to traffic
from or to remote clusters.  In most environments those NAT gateway addresses are used for
all non-local cluster traffic.  Without very complicated NAT configuration the inter-cloud
traffic rules could only be expressed cluster wide.

In a NAT environment it is also easy to express client side egress rules to any public facing and
change invariant IPs.

To continue by going through a network policy 
[example](../Multicloud%20Automation/examples/dmvpn_eks_ccp_calico_stars.md)
return to the main page.

