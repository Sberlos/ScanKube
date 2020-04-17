## Node

Formally a Node is an API object created outside the cluster representing an instance.
More practically we can consider that a machine.
The Master Node must be Linux but the workers can also be Windows Server 2019.

Every Node is contacted by [kube-apiserver](kube-apiserver.md) every _NodeLease_ time (default to 5 minutes), if it does not respond, it schedules the node for deletion and change the _NodeStatus_ from _ready_ to [deleted?].

_The pods will be evicted once connection is reestablished. They are no longer forcibly removed and rescheduled by the cluster._
[Not sure to understand it]

Every node object is part of the `kube-node-lease` namespace.
