== Services ==

* Regroups and connects (and reconnects if there are deaths and successives respownings) [Pods](pod.md) together (it can even connects pods to resources outside the cluster)
* It exposes the pods to the Internet 
* Define Pod access policy [*how?* [[#q1|q1]]]
* It allows to decouple settings [*how?*]

It is the incarnation of a Microservice.

A Service also handles access policies for inbound requests, useful for resource control as well as for *security*.
_This needs clarification for the first part (in practice) and it's useful for the security part._

[Labels](label.md) are used to dermine wich [Pods](pod.md) should receive traffic from a Service.

Service types:
* ClusterIP (default, provides only access internally, except if you create manually an external endpoint)
* NodePort (good for debugging of if you require a static ip)
* LoadBalancer (intended for passing requests to cloud providers, even without the address is public and packets are spread among the [Pods](pod.md))
* ExternalName (it is used to connect to external services, it create an alias at DNS level)

`kubectl proxy` creates a local service to access a `clusterIP` (troubleshotting or development).

:q1: A service can have multiples pods, it choses which pod as a scheduler (don't think so as there is already a scheduler) or it routes the traffic for the specific resource? Like the container with the web app needs the database here is it the route to it (probably this second option) ?
