## Kube controller manager ##

The kube-controller-manager is a core control loop daemon which interacts with the [kube-apiserver](kube-apiserver.md) to determine the state of the cluster.
If the state does not match, the manager will contact the necessary controller to match the desired state.
There are several [controllers](controller.md) in use, such as endpoints, namespace, and replication.
The full list has expanded as Kubernetes has matured.
**Find the full list**
