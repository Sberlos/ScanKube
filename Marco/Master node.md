# Master Node

## kube-apiserver
All calls, both internal and external traffic are handled via this agent. All actions are accepted and validated by this agent and it is the only connection to the **etcd** database. As a result it acts as a master process for the entire cluster, and acts as a front-end of the cluster’s shared state.

## kube-scheduler

The **kube-scheduler** uses an algorithm to determine which node will host a Pod of containers. The scheduler will try to view available resources (such as volumes) to bind, and then try and retry to deploy the Pod based on availability and success.

There are several ways you can affect the algorithm, or a custom scheduler could be used instead. You can also bind a Pod to a particular node, though the Pod may remain in a pending state due to other settings.

One of the first settings referenced is if the Pod can be deployed within the current quota restrictions. If so, then the taints and tolerations, and labels of the Pods are used along with those of the nodes to determine the proper placement.

## etcd database

The state of the cluster, networking and other persistent information is kept in an **etcd** database, or more accurately a b+tree key-value store. Rather than find and change an entry, values are always appended to the end. Previous copies of the data are then marked for future removal by a compaction process. 

Simultaneous requests to update a value all travel via the **kube-apiserver**, which then passes along the request to **etcd** in a series.

There is a master database along with possible followers. They communicate to each other on an ongoing basis to determine which will be master and determine another in the event of failure.

