## Volume ##

The main purpose of a Volume is to save data longer than the lifetime of a container.
It get binded to a pod and not to a container, meaning that you can restart/take down containers but the volume will be intact.

A volume is simply a directory made available to containers in a Pod.
There are many volume types (Ceph, NFS, Google0s gcePersistentDisk, ...).

A volume can be accessed by multiple pods with all write access, not concurrency check is made by kubernetes so be careful (it can be done by the volume itself tho).

### Container Storage Interface (CSI) ###

The Container Storage Interface (CSI) adoption enables the goal of an industry standard interface for container orchestration allow access to arbitrary storage systems.
Currently volume plugins are ”in-tree”, meaning they are compiled and built with the core Kubernetes binaries.
This ”out-of-tree” object will allow storage vendors to develop a single driver and allow the plugin to be containerized.
This will replace the existing Flex plugin which requires elevated access to the host node, a *large security concern*.

### Persistent Volumes (PV) ###

If you want a storage to have a lifetime different from a [Pod](pod.md) you can use `Persistent Volumes`.
A pod can claim those volumes via a `Persistent Volume Claim` (PVC).
Many pods can use the same Persistent Volume [*simultaneously?*]

The interaction with a PV has multiple phases: [_copied from slide 191/458_]
* *Provisioning* can be from PVs created in advance by the cluster administrator, or requested from a dynamic source such as the cloud provider.
* *Binding* occurs when a control loop on the master notices the PVC, containing an amount of storage, access request, and optionally a particular StorageClass.
  The watcher locates a matching PV or waits for the StorageClass provisioner to create one.
  The PV must match at least the storage amount requested, but may provide more.
* The *use* phase begins when the bound volume is mounted for the Pod to use, which continues as long as the Pod requires.
* *Releasing* happens when the Pod is done with the volume and an API request is sent deleting the PVC.
  The volume remains in the state from when the claim is deleted until available to a new claim.
  The resident data remains depending on the persistentVolumeReclaimPolicy.
* The *reclaim* phase has three options: _Retain_ which keeps the data intact allowing for an admin to handle the storage and data.
  _Delete_ tells the volume plug-in to delete the API object as well as the storage behind it.
  The _Recycle_ option runs an rm -rf /mountpoint then makes it available to a new claim.
  With the stability of dynamic provisioning the _Recycle_ is planned to be deprecated.

_PV are not namespaces objects but pvc are._

```
kind: PersistentVolume
apiVersion: v1
metadata:
        name: 10Gpv01
        labels:
                type: local
spec:
        capacity:
                storage: 10Gi
        accessModes:
                - ReadWriteOnce
        hostPath:
                path: "/somepath/data01"
```

A pvc looks like this:
```
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
        name: myclaim
spec:
        accessModes:
                - ReadWriteOnce
        resources:
                requests:
                        storage: 8Gi
```

And then it will be used like this in the Pod:
```
spec:
        containers:
...
        volumes:
                - name: test-volume
                persistentVolumeClaim:
                        claimName: myclaim
```

#### Dynamic Provisioning ####

Dynamic Provisioning allow the cluster to request storage from an exterior, pre-configured, source.
This means that you don't have to pre-create PVs.
It uses the `StorageClass` API object where the admin can define a persistent volume provisioner of a certain type.

Example using GCE (Google something):
```
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast    # Could be any name
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
```

### Integration with Pods ###

A [Pod](pod.md) can declare the volumes that he needs and where to find them.
It's required that you assign to each of them a name, a type and a mount point.
As it can be available to multiple containers inside the [Pod](pod.md) you can use them as container-container communication.

A [Pod](pod.md) requires an access with a set of permission, `access mode`, the request is fulfilled with a set of permissions that is equal or greater than the requested ones.
The cluster groups volumes with the same mode together, then sorts volumes by size from smallest to largest.
The claim is checked against each in that access mode group until a volume of sufficient size matches.
The three access modes are *RWO* (`ReadWriteOnce`), which allows read-write by a single node, *ROX* (`ReadOnlyMany`), which allows read-only by multiple nodes, and *RWX* (`ReadWriteMany`) which allows read-write by many nodes.

```
apiVersion: v1
kind: Pod
metadata:
        name: busybox
        namespace: default
spec:
        containers:
        - image: busybox
          name: busy
          command:
            - sleep
            - "3600"
          volumeMounts:
          - mountPath: /scratch
            name: scratch-volume
        volumes:
        - name: scratch-volume
          emptyDir: {}
```

Note: the `emptyDir` in this example is a special type of storage that is inside the [Pod](pod.md) in the container shared space and thus not persistent.

Complex example:

```
The Pod configuration could also be as complex as this:
volumeMounts:
        - name: Cephpd
        mountPath: /data/rbd
  volumes:
    - name: rbdpd
      rbd:
        monitors:
        - '10.19.14.22:6789'
        - '10.19.14.23:6789'
        - '10.19.14.24:6789'
        pool: k8s
        image: client
        fsType: ext4
        readOnly: true
        user: admin
        keyring: /etc/ceph/keyring
        imageformat: " 2"
        imagefeatures: " layering"
```

### Volume types ###

[Slide 189/458 - Choose to import as table?]
