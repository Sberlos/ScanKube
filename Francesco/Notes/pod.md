## Pod ##

### General description ###

A Pod is composed by one or more containers and it's the smallest unit of the cluster.
Every Pod has one and only one shared IP addres for the whole Pod and a set of data volumes associated with it.

All the containers are started in parallel inside a Pod.
The containers inside the Pod can comunicate through IPC, the loopback interface or a shared filesystem.

Usually a Pod has one application container in it, additionally it can have something called _sidecar_, a [container](container.md) that does a helper job (logging, responding to requests, ...).

They are created from a [PodSpec](podspec.md).

### Networking ###

Every container in the Pod shares the same network namespace.
This is also shared with the *pause container* that gives a lifetime IP address to the pod.
But it's configured by [kubelet](kubelet.md) along with [kube-proxy](kube-proxy.md).
The `NodePort` service connects the Pod to the outside network. [*always?*]

When you create a [service](service.md) it is created at the same time an `endpoint`, it is the ip addres of the pod with the port of the application.
The service connects the trafic from the `endpoint` to the node translating the high port number that it is used at the node level to the `endpoint` (_in some way it's doing a NAT_).

The [kube-controller-manager](kube-controller-manager.md) checks (using watch loops) if `endpoints` or [services](service.md) are needed, along with updates and deletions.

#### Pod-to-Pod Communication ####

Kubernetes expects that you put in place the pod to pod comunication, it doesn't do it for you.
This means that you have to user either a physical network infrastructure or a software defined overlay (like Weave, Calico, Flannel or Romana).
As every Pod has its IP address (as the node) we can route them without NAT.
