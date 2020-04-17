## PodSpec ##

The PodSpec is a document describing a [Pod](pod.md) to be created.
It has only 4 required fields:
* apiVersion
* kind (The type of object to create)
* metadata (At least a name)
* spec (What to create and parameters)

Simple example in YAML format:
```
apiVersion: v1
kind: Pod
metadata:
        name: firstpod
spec:
        containers:
        - image: nginx
          name: stan
```

You can create a pod via file with:
```
kubectl create -f podFile.yaml
```
