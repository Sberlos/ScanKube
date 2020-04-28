## Ephemeral container ##

That's a container that you can attach to a running [Pod](pod.md).
The purpose is intended for troubleshooting when the `exec` command is not sufficient (or you don't have a shell).

It's important to notice that it's still in alpha (since v.16)

In order to use it you do:
```
kubectl debug buggypod --image debian --attach
```
or
```
kubectl attach -it example-pod -c debugger
```
If you have already defined the `debugger` _Ephemeral Container_.

### Requisites ###

In order to this to work the corresponding `feature gate` needs to be enabled.

### Example Config ###

```
{
        "apiVersion": "v1",
        "kind": "EphemeralContainers",
        "metadata": {
                "name": "example-pod"
        },
        "ephemeralContainers": [{
                "command": [
                        "sh"
                ],
                "image": "busybox",
                "imagePullPolicy": "IfNotPresent",
                "name": "debugger",
                "stdin": true,
                "tty": true,
                "terminationMessagePolicy": "File"
        }]
}
```
