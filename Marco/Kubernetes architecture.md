# Kubernetes Architecture

Kubernetes is made of a central manager (aka master) and some worker nodes. The manager runs an API server, a scheduler, various controllers and a storage system to keep the state of the cluster, container settings, and networking configuration.

Kubernetes exposes an API via the API server. You can communicate with the API using a local client called **kubectl** or you can write your own client and use **curl** commands. The **kube-scheduler** is forwarded the requests for running containers coming to the API and finds a suitable node to run that container. Each node in the cluster runs two processes, a **kubelet** and a **kube-proxy**. The **kubelet** receives requests to run the containers, manages any resources necessary and watches over them on the local node. **kubelet** interacts with the local container engine (Docker by default). The **kube-proxy** creates and manages networking rules to expose the container on the network.

## Terminology

- Pod: one or more containers sharing IP address, access to storage and namespace
- Labels: key/value pairs that are attached to objects, such as pods. Labels enable users to map their own organizational structures onto system objects in a loosely coupled fashion, without requiring clients to store these mappings. Labels allow for efficient queries and watches and are ideal for use in UIs and CLIs.
- Taints/Tolerations: Taints and tolerations work together to ensure that pods are not scheduled onto inappropriate nodes. One or more taints are applied to a node; this marks that the node should not accept any pods that do not tolerate the taints. Tolerations are applied to pods, and allow (but do not require) the pods to schedule onto nodes with matching taints.
- Annotations: key/value pairs that are attached to objects, such as pods. Labels can be used to select objects and to find collections of objects that satisfy certain conditions. In contrast, annotations are not used to identify and select objects. The metadata in an annotation can be small or large, structured or unstructured, and can include characters not permitted by labels.
- Controllers: control loops that watch the state of your cluster, then make or request changes where needed. Each controller tries to move the current cluster state closer to the desired state. The controller might carry the action out itself; more commonly, in Kubernetes, a controller will send messages to kube-apiserver that have useful side effects.

