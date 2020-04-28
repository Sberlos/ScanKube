## StatefulSet ##

This object is similar to deployments, the difference is that it consider each [Pod](pod.md) composing it as unique and provides ordering to [Pod](pod.md) deployment.
This means that the next [Pod](pod.md) in order is not started until the previous one is running and ready.
The consequence is that [Pods](pod.md) are not deployed in parallel.
