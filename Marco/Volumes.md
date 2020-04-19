# Volumes

A volume is a directory, possibly pre-populated, made available to containers in a Pod. The creation of the directory, the backend storage of the data, and the contents depend on the volume type. A Kubernetes Volume shares the Pod lifetime, not the containers within. Should a container terminate, the data would continue to be available to the new container.

A Pod specification can declare one or more volumes and where they are made available. Each requires a name, a type, and a mount point. The same volume can be made available to multiple containers within a Pod, which can be a method of container- to-container communication. A volume can also be made available to multiple Pods, with each given an access mode to write. There is no concurrency checking which means data corruption is probable unless outside locking takes place.

Part of a Pod request is a particular access mode. As a request the user may be granted more, but not less access, though a direct match is attempted first. The cluster groups volumes with the same mode together, then sorts volumes by size from smallest to largest. The claim is checked against each in that access mode group until a volume of sufficient size matches. The three access modes are RWO (ReadWriteOnce), which allows read-write by a single node, ROX (ReadOnlyMany), which allows read-only by multiple nodes, and RWX (ReadWriteMany) which allows read-write by many nodes.

## Persistent volumes

A *PersistentVolume* (PV) is a piece of storage in the cluster that has been provisioned by an administrator or dynamically provisioned using Storage Classes. It is a resource in the cluster just like a node is a cluster resource. PVs are volume plugins like Volumes, but have a lifecycle independent of any individual Pod that uses the PV. This API object captures the details of the implementation of the storage, be that NFS, iSCSI, or a cloud-provider-specific storage system.

A *PersistentVolumeClaim* (PVC) is a request for storage by a user. It is similar to a Pod. Pods consume node resources and PVCs consume PV resources. Pods can request specific levels of resources (CPU and Memory). Claims can request specific size and access modes (e.g., they can be mounted once read/write or many times read-only).

There are several phases to persistent storage:

- **Provisioning** can be from PVs created in advance by the cluster administrator, or requested from a dynamic source such as the cloud provider.
- **Binding** occurs when a control loop on the master notices the PVC, containing an amount of storage, access request, and optionally a particular StorageClass. The watcher locates a matching PV or waits for the StorageClass provisioner to create one. The PV must match at least the storage amount requested, but may provide more.
- The **use** phase begins when the bound volume is mounted for the Pod to use, which continues as long as the Pod requires.
- **Releasing** happens when the Pod is done with the volume and an API request is sent deleting the PVC. The volume remains in the state from when the claim is deleted until available to a new claim. The resident data remains depending on the persistentVolumeReclaimPolicy.
- The **reclaim** phase has three options: **Retain** which keeps the data intact allowing for an admin to handle the storage and data. **Delete** tells the volume plug-in to delete the API object as well as the storage behind it. The **Recycle** option runs an **rm -rf /mountpoint** then makes it available to a new claim. With the stability of dynamic provisioning the **Recycle** is planned to be deprecated.