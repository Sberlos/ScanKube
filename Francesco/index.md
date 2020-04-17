# Thesis #

## Schedule ##

### Initial One ###

* 9.3 - 18.3 Study of Kubernetes internals
* 19.3 - 25.3 Study of the container Runtime Interface (CRI)
  - Namespaces management
  - Syscalls
* 26.3 - 1.4 Analysis of the way Kubernetes manages CRIs
* 2.4 - 5.4 Analysis of CRI architecture
* 6.4 - 26.4 Identification of attack vectors
  - Attack vectors in CRI
  - Attack vectors in Kubernetes
* 27.4 - 10.5 Writing of a Proof of Concept for the attacks
* 11.5 - 24.5 Report writing/finalisation

### Updated One ###

* 9.3 - 25.3 Study of Kubernetes internals
* 26.3 - 8.4 Study of the container Runtime Interface (CRI)
  - Namespaces management
  - Syscalls
* 9.4 - 10.4 Analysis of the way Kubernetes manages CRIs
* 11.4 - 13.4 Analysis of CRI architecture
* 14.4 - 30.4 Identification of attack vectors
  - Attack vectors in CRI
  - Attack vectors in Kubernetes
* 31.4 - 10.5 Writing of a Proof of Concept for the attacks
* 11.5 - 24.5 Report writing/finalisation

## TODO ##

* Avere un Cluster su (anche con i default va bene) [**FATTO**]
* Riprendere Go [in corso]
* Riguardare un po' cosa abbiamo fatto lo scorso semestre [in corso]

## Kubernetes ##

### Design ###

#### Architecture ####

* [[kubelet]]
* [[kube-proxy]]
* [[kube-scheduler]]
* [[kube-controller-manager]]
* [[cloud-controller-manager]]
* [[kube-apiserver]]
* [[etcd]]
* kubectl
* [[addons|Addons]]

#### Elements / Objects (?) ####

* [[service|Services]]
* [[controller|Controllers]]
* [[pod|Pods]]
* [[container|Containers]]
* [[init container|Init Containers]]
* [[ephemeral container|Ephemeral Containers]]

* [[deployment|Deployments]]
* [[job|Jobs]]
* [[daemonset|DaemonSets]] [controller]
* [[statefulset|StatefulSet]]

* [[label|Label]]

* [[volume|Volumes]]
* [[configmap|ConfigMaps]]
* [[ingress|Ingress]]

* [[custom resource|Custom Resources]]

#### Machines level components ####

* [[node|Node]]
* Master Node
* [[worker node|Worker Node]]

### Topics ###

* [[security|Security]]
* [[helm|Helm]]

#### Random ####

* Know the deep difference with pod, service, replicationcontroller, deployement and replicaset. Those are the things that you can expose via
  ```
  kubectl expose
  ```
  You can always append the -h flag for help and description

### Usage ###

* [[kubectl]]

#### To be placed ####

* Kubernetes does not have a cluster-wide logging, Fluentd is used.
* Per-deployment settings override the global namespace settings. [Deployment and namespace]
* *At pages 151-155/458 you have a description of all fields in the yaml/json spec file for a deployment, replicaset and pods.*

* `kubectl drain nodeName` is used to drain all the containers from _nodeName_ to the current node. See pages 103-104/458
* Startup sequence: 
  1. systemd starts kubelet.service
    * Uses `/etc/systemd/system/kubelet.service.d/10-kubeadm.conf`
    * Uses `/var/lib/kubelet/config.yaml` config file
    * *staticPodPath* set to `/etc/kubernetes/manifests/`
  2. *kubelet* creates all pods from *.yaml in directory `/etc/kubernetes/manifests/`
    * [[kube-apiserver]]
    * [[etcd]]
    * [[kube-controller-manager]]
    * [[kube-scheduler]]
  3. [[kube-controller-manager]] control loops use [[etcd]] data to start rest

### Tools ###

* [Minikube](Minikube.md)
* [Microk8s](Microk8s.md)

### Resources ###

Rename this section and reorganize

* [Resources](resources.md) -- Links that could be useful
* Random Notes
