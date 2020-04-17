## Container ##

Through Kubernetes we cannot directly interact with them but we manage the resources limits of them.
This is done in the _resource_ section of the PodSpec (this interacts with the container engine) or with the creation of a `ResourceQuota` object.
The second option gives more possibilities than just the CPU and memory limits that you can specify in the PodSpec.

### Container Network Interface (CNI) ###

It is a specification to write plugins that configure container networking and deallocate resources when the container is deleted.
It has a set of libraries associated and is language agnostic.

Its aim to provide a common interface between the various networking solutiosn and container runtimes.

Configuration example:
```
{
        "cniVersion": "0.2.0",
        "name": "mynet",
        "type": "bridge",
        "bridge": "cni0",
        "isGateway": true,
        "ipMasq": true,
        "ipam": {
                "type": "host-local",
                "subnet": "10.22.0.0/16",
                "routes": [
                        { "dst": "0.0.0.0/0"}
                ]
        }
}
```

Resource: https://github.com/containernetworking/cni 
