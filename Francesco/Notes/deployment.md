## Deployments ##

A Deployment is a controller which manges the state of [ReplicaSets](replicaset.md) and the pods within.
On the notes: _Unless you have a good reason, use a deployment_

You use Deployments in order to do server side rolling updates.
This means that you can edit the Deployment spec file and then call `kubectl apply` or `kubectl edit` directly and the cluster will adapt to reflect this new spec.
In practice the [ReplicaSets](replicaset.md) are adapted to reflect this new state and they are the responsible for mutating the cluster.
[See slide 150/458]
