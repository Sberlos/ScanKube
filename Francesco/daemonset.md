## DaemonSet ##

This controller allows you to run a copy of a specific [Pod](pod.md) on every node.
This is useful for logging pods or similar that you want everywhere.
Of course there is a setting for excluding certains nodes.
It takes care both of the starting of the [Pod](pod.md) when a new node is added and of the deletion when the node is removed from the cluster.

### Commands and abbreviation ###

```
kubectl get daemonsets
kubectl get ds
```
