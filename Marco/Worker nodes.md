# Worker Nodes

All worker nodes run the **kubelet** and **kube-proxy**, as well as the container engine such as **Docker** or **rkt**. Other management daemons are deployed to watch these agents or provide services not yet included with Kubernetes.

The **kubelet** interacts with the underlying **Docker** engine also installed on all the nodes and makes sure that the containers that need to run are actually running. The **kube-proxy** is in charge of managing the network connectivity to the containers. It does so through the use of **iptables** entries.

