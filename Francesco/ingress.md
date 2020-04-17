## Ingress ##

An `Ingress Controller` is a daemon running in a [Pod](pod.md) and it accomplish the same function of exposing a containerized application outside the cluster as a [Service](service.md).
It is more efficient as instead of having many services you can route traffic based on request host or path centralizing many services to a single point.

The `Ingress Controller` does not run as part of [kube-controller-manager](kube-controller-manager.md) binary.
You can deploy multiple controllers, each with unique configurations.
A controller uses Ingress Rules to handle traffic to and from outside the cluster.
It works by watching the `/ingress` endpoint on the API server wich is found under `networking.k8s.io/v1beta1` group, for new objects.

Incoming traffic should use annotations to select the proper controller.

Supported controllers:
* nginx
  - Easy integration with RBAC
  - Uses the annotation `kubernetes.io/ingress.class: "nginx"`
  - L7 traffic requires the proxy-real-ip-cidr setting
  - Bypasses kube-proxy to allow session affinity
  - Does not use conntrack entries for iptables DNAT
  - TLS requires host field to be defined
  - Deployment made easy thanks to this file: https://github.com/kubernetes/ingress-nginx/tree/master/deploy
* GCE [*Slide 221/458* not going in details here]
  - The controller is called *glbc* (Google Load Balancer Controller) and must be created and started beforehand
  - Multi-pool path
  - ...

But any tool capable of reverse proxy should work.

### Example spec ###

```
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
name: ghost
spec:
rules:
        - host: ghost.192.168.99.100.nip.io
http:
paths:
        - backend:
                        serviceName: ghost
                        servicePort: 2368
```

You can manage Ingress resources like you do pods, deployments, services, etc.

Sample controller deployment: https://github.com/kubernetes/ingress-nginx/tree/master/deploy

### Service Mesh ###

If you need more complex interactions you can use a service mesh.
A service mesh consists of edge and embedded proxies communicating with each other and handing traffic based on rules from a control plane.
Various options are available including Envoy, Istio, and linkerd.
