# Minikube #

## What ##

Tool that launches a single node cluster in virtualbox.
Apparently it's limited but useful for learining and tests.

## Commands ##

Start the cluster
```
Minikube start --driver=virtualbox
```
Stop the cluster
```
Minikube stop
```

Curl the kubernetes API (instructions found here: https://stackoverflow.com/questions/40720979/how-to-access-kubernetes-api-when-using-minkube [third answer with the corrections of the second comment])
Find the ip address:
```
Minikube ip
```
Get the secret:
```
export secret=$(kubectl get serviceaccount default -o jsonpath='{.secrets[0].name}')
```
Save the token:
```
kubectl get secret $secret -o jsonpath='{.data.token}' | base64 --decode > token
```
Curl the API (I already substituted the ip address with the one found with `Minikube ip` and the location of my token file):
```
curl -v -k -H --cacert ~/.minikube/ca.crt -H "Authorization: Bearer $(cat token)" "https://192.168.99.103:8443/api/v1/"
```

## Notes? ##

If you ssh inside the vm with `minikube ssh` you are the user `docker` that's member of the wheel group, therefore you can use sudo and as it's configured to not ask passwords you can do watherver you want.

I think this is only for minikube as you have to access the box being able to do everything but we could check if things like that are exploitable in real case scenarios.

## Links ##

Examples link: https://minikube.sigs.k8s.io/docs/examples/
