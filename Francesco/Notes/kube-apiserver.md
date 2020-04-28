## kube-apiserver ##

It's a REST endpoint that controls the whole cluster, is the only one connected to the [etcd](etcd.md) database.
It's the master process and is the frontend for the shared state.
It can be considered the master for the cluster, all components work through it.
All call (both internal and external traffic) are handled via this agent.

Slide 76(458): Starting as an alpha feature in v1.16 is the ability to separate user-initiated traffic from server-initiated traffic. Until these fea-
tures are developed most network plugins commingle the traffic, which has performance, capacity, and security ramifications.
**Check in particular the security ramifications**
