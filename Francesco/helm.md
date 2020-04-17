## Helm ##

### Overview ###

Helm is like a package manager for Kubernetes, you can deploy a whole application (that includes several manifests) with a simple command.
The application is condensed in a single tarball, a `chart`, that can considered a package.
The `chart` is stored in a repository.

The server responsible for this runs in your cluster but your client (the one deploying the `chart`) can be anywhere (your laptop).
Via the client you can browse repositories in order to see published `charts`.

### v2 ###

The helm version 2 uses a Tiller pod with elevated permissions to deploy objects in the cluster.
This has led to a lot of issues with security and cluster permissions, for this reason the new version 3 does not deploy a pod.

In version 2 there where two components: the Helm client and the Tiller server in the cluster.

Calling
```
helm init
```
will initialize it.

The client communicates with Tiller with port forwarding, hence there is no service exposing it.

### v3 ###

Many changes, notably no more Tiller [Pod](pod.md).
Additionally the update is performed using a 3-way strategic merge patch (add the check of live state of objects).
Among other changes software installation no longer generates a name automatically.
One must be provided, or the `--generated-name` option must be passed.

Helm v3 doesn't need to be initialized, you just need the binary or package in you master node.

### Usage ###

`helm` is the command for using Helm.

#### Repository management ####

You can add a repo with
```
helm add repoName https://urloftherepo.com
```
And then you can list the repos that you have added with:
```
helm repo list
```
And then you can search in your repos based on a keyword:
```
helm search keyword
```

Additionally you can search in the _Helm Hub_ or in an instance of _Monocular_:
```
helm search hub keyword
```

#### Installation ####

Installing is simple:
```
helm install repoName/chartName
```
then you can list/delete/upgrade/roll-back the release.
list:
```
helm list
```
update:
```
helm update repo
```
uninstall:
```
helm uninstall nameGivenAtInstallation
```
