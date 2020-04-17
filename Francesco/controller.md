## Controllers ##

Controllers are control loops that watch the state of your cluster, then make or request changes where needed.
Each controller tries to move the current cluster state closer to the desired state.
There are many controllers with Kubernetes and you can create your own.
The basic concept is that they are *watch based control loop monitoring delta*, in practice the check if there are requested[*?*] modifications and then it tries to apply them.
They work using a `DeltaFIFO` queue, they get a stream of deltas and they apply them to the specifications and then adjust the objects inside the cluster.

There are two types of agents that report the state of the cluster: *[check this bit]*
* `Informer`
* `SharedInformer`

Both request the state of a specific object via API calls and then store it in cache.
The difference between them is that the `SharedInformer` are often used by multiple other objects creating a shared chache of the state for multiple requests.

The `Workqueue` is the responsible for handing out the tasks to various workers using a key [*?*].
For this, the standard Go work queues are usually used.

Shipped controllers:
* `replication`
* `endpoints`
* `namespace`
* `serviceaccounts`
