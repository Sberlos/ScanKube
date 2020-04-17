## Etcd ##

Key-value store, the state of the cluster is saved here (with the networking information and other persistent information)
When you do a request for a modification to the [kube-apiserver](kube-apiserver.md) it is checked the version where you changes apply against.
If two requests come simultaneously the first one is allowed and the second receives an error 409.
It's important to note that it shed the oldest version of superseded data.
This works by appending the new data (not replacing) at the end and the marking the old version of the entry added as to be removed.
There could be a configuration with _master_ and _followers_ instances.

### Implementation details ###

It's a multiversion persistent b+tree key-value store with append only and regular compaction.
It has a distributed consensus protocol for leadership.
