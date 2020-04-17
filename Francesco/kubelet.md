## Kubelet ##

It interacts with the underlying container engine and runs on each node.
This means making sure that all the containers that needs to run are actually running.
In practice it accepts the API calls for Pod specifications and tries to configure the local node until it corresponds to the configuration required.

It is responsibile for creating or giving access to storage (it mounts the volumes), [secrets](secret.md) or [ConfigMaps](configmaps) to [Pods](pod.md).

Additionally is responsible to the comunication in the other way, this means that it reports the status of [Pod](pod.md) and [node](node.md) to the cluster.

*Slide 81-458 it says it sends back status to the kube-apiserver.*
*It talks about the storage/secrets/configmaps or reporting the status as we mentioned above?*

### Questions ###

* It is contacted directly with kubectl? Or it finds by himself the configuration somewhere(you send it to the node and it reads it locally)?
