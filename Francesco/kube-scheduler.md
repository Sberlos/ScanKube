## Kube-scheduler ##

*INFO This could be expanded but don't think it's useful.*

Scheduler that choses which [Node](node.md) will host a [Pod](pod.md) of containers.
It tries and retry based on success and resource availability.
Can be influenced by custom policies (or you can have a custom scheduler).
This means that you can set affinity rules in order to try to place pods on specific nodes and you can user [Taints](taint.md) to repel pods *[The last bit needs clarification]*

I should have one section for type?

### Priorities ###

Set of **priority functions** used to weight resources.
The highest value node is chosen by the scheduler.
By default the scheduler will chose the node with the least amount of [Pods](pod.md).

List at: `master/pkg/scheduler/algorithm/priorities`

`PriorityClasses` can be used to allocate and preemt other pods and a `Pod Distruption Budget` can be used to limit disruption by preemtion.

### Taint ###

A node with a particular `taint` will repel [Pods](pod.md) without `tolerations` for that `taint`.
They are expressed as key#value:*effect*.
The effect can be one of the following:
* NoSchedule (no schedule of new pods but existing continue to run)
* PreferNoSchedule (scheduler will avoid unless no other option, existing unaffected)
* NoExecute (no future pods scheduled and running will be evacuated unless toleration)

Only nodes can be tainted but multiple are possible on a single node.

### Tolerations ###

Pod setting to run on `tainted` nodes, it has the same *effects* as node taints.

### Stuff that has to be reorganized ###

One of the first settings referenced is if the [Pod](pod.md) can be deployed within the current quota restrictions.
If so, then the [Taints](taint.md) and [Tolerations](toleration.md), and [Labels](label.md) of the [Pods](pod.md) are used along with those of the nodes to determine the proper placement.
