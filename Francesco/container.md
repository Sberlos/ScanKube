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

### Container Level Architecture

#### Container Engine

##### Overview

A container engine is a piece of software that accepts user requests, including command line options, pulls images, and from the end user’s perspective runs the container.
Most containers engines don't actually run the containers, they rely on an OCI compliant runtime like runc.

The usual tasks of the Container Engine are:
* Handling user input
* Handling input over an API often from a Container Orchestrator
* Pulling the Container Images from the Registry Server
* Expanding decompressing and expanding the container image on disk using a Graph Driver (block, or file depending on driver)
* Preparing a container mount point, typically on copy-on-write storage (again block or file depending on driver)
* Preparing the metadata which will be passed to the container Container Runtime to start the Container correctly
* Using some defaults from the container image (ex.ArchX86)
* Using user input to override defaults in the container image (ex. CMD, ENTRYPOINT)
* Using defaults specified by the container image (ex. SECCOM rules)
* Calling the Container Runtime

##### List of Container Enginges

* Docker
* RKT (doesn't use runc)
* CRI-O
* LXD (doesn't use runc)
* Many Cloud providers,PaaS and Container Platforms have their own built-in container engines 

The OCI standard is used to allow interoperability.

#### Container Runtime

A container runtime a lower level component typically used in a Container Engine but can also be used by hand for testing.
The Open Containers Initiative (OCI) Runtime Standard reference implementation  is runc.
This is the most widely used container runtime, but there are others OCI compliant runtimes, such as crun, railcar, and katacontainers.
Docker, CRI-O, and many other Container Engines rely on runc.

The container runtime is responsible for:
* Consuming the container mount point provided by the Container Engine (can also be a plain directory for testing)
* Consuming the container metadata provided by the Container Engine (can be a also be a manually crafted config.json for testing)
* Communicating with the kernel to start containerized processes (clone system call)
* Setting up cgroups
* Setting up SELinux Policy
* Setting up App Armor rules

Resource: https://developers.redhat.com/blog/2018/02/22/container-terminology-practical-introduction/#h.6yt1ex5wfo55
