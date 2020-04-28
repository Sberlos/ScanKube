## Security ##

### Secrets ###

They are just base64 encoded strings therefore there is no real security if you don't create the `EncriptionConfiguration` with key and identity and you set the `--encryption-provider-config` flag set to a pre-configured provider such as `aescbc` or `ksm`. [*What are those?*]
Multiple keys are possible and you can rotate them.

You can create a secret with (example): [TODO dig deeper]
```
kubectl create secret generic mysql --from-literal=password=root
```

Or manually using `base64`.

A secret can be used as an environment variable in a *Pod*, example:
```
...
spec:
containers:
- image: mysql:5.5
  env:
  - name: MYSQL_ROOT_PASSWORD
    valueFrom:
        secretKeyRef:
                name: mysql
                key: password
     name: mysql    # weird alignment here but it's like that on the slides, where is right?
```

Secrets are stored in the *tmpfs* storage on the host node and are only sent to the host running [Pod](pod.md).

Additionnally a secret can also be mounted as volume in a [Pod](pod.md) manifest:
```
...
spec:
        containers:
        - image: busybox
          command:
                - sleep
                - " 3600"
          volumeMounts:
          - mountPath: /mysqlpassword
            name: mysql
          name: busy
        volumes:
        - name: mysql
                secret:
                        secretName: mysql
```

Secrets are protected because you simply don't let the pods that should not see them have access to them.
That's the security model.
The problem is that if you compromise one Pod you see al the secrets and usually even the ones to talk with the cluster directly.
There are entreprise solutions (Hashicorp Vault, AquaSec, TwistLock) that tries to mitigate this problem in addition to the standard way of encrypting them (that has the overhead problem).

#### Resources ####

Hashicorp Vault, AquaSec, TwistLock (mentioned above)

### Accessing the API ###

Three steps in order to access the API to perform any action:
* [Authentication](#authentication)
* [[security#Authorization|Authorization]] (ABAC or RBAC, check if the user has permission to do that action)
* [[security#Admission Control|Admission Control]] (check the actual content of the objects being created and validate them before admitting the request)
Resource for this: https://kubernetes.io/docs/admin/accessing-the-api/

In addition the request come using TLS.

#### Authentication ####

Three main points to remember:
* You can use one or more `Authenticator Modules`:
        * x509 Client Certs
        * Static Token, Bearer or Bootstrap Token
        * Static Password File
        * Service Account and OpenID Connect Tokens
        * Webhooks
* Users are not created by the API, but should managed by an external system
* System accounts are used by processes to access the API (https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/ )

Main resource: https://kubernetes.io/docs/admin/authentication/

#### Authorization ####

Once a request is authenticated, it needs to be authorized to be able to proceed through the Kubernetes system and perform its intended action.
There are three main authorization modes and two global Deny/Allow settings.

They can be configured as [kube-apiserver](kube-apiserver.md) startup options:
* `--authorization-mode=ABAC`
* `--authorization-mode=RBAC`
* `--authorization-mode=Webhook`
* `--authorization-mode=AlwaysDeny`
* `--authorization-mode=AlwaysAllow`

The authorization modes implement policies to allow requests.
Attributes of the requests are checked against the policies (e.g. user, group, namespace, verb). *[Needs clarification]*

##### ABAC (Attribute Based Access Control) #####

Used prior to RBAC (that is becoming the default).
Policies are defined in a JSON file and referenced to by a [kube-apiserver](kube-apiserver.md) startup option:
```
--authorization-policy-file=my_policy.json
```
Simple example (here Alice can do anything to all resources):
```
{
        "apiVersion": "abac.authorization.kubernetes.io/v1beta1",
        "kind": "Policy",
        "spec": 
                {
                        "user": "alice",
                        "namespace": "*",
                        "resource": "*",
                        "apiGroup": "*"
                }
}
```
More examples at https://kubernetes.io/docs/reference/access-authn-authz/abac/#examples

##### RBAC (Role Based Access Control) #####

Elements:
* Resources and Operations (verbs)
* Rules
* Roles and ClusterRoles
* Subjects
* RoleBindings and ClusterRoleBindings

[TODO rewrite the next block with my words/Choose if I want resources and operations in bold]

All `resources` are modeled API objects in Kubernetes from [Pods](pod.md) to Namespaces.
They also belong to API Groups such as `core` and `apps`.
These resources allow `operations` such as *Create*, *Read*, *Update*, and *Delete* (*CRUD*).
Operations are called verbs inside YAML files.

*Rules* are operations which can act upon an API group.
*Roles* are a group of rules which affect, or scope, a single namespace, whereas *ClusterRoles* have a scope of the entire cluster.

Each operation can act upon one of three *subjects* which are User Accounts which don’t exist as API objects, `Service Accounts` and `Groups` which are known as `clusterrolebinding` when using [kubectl](kubectl.md).

*RBAC* is writing rules to allow or deny operations by users, roles or groups upon resources.

Main resource: https://kubernetes.io/docs/reference/access-authn-authz/rbac/ _A lot more there_ 

###### RBAC Process Overwiew ######

* Determine or create namespace
* Create certificate credentials for user
* Set the credentials for the user to the namespace using a context
* Create a role for the expected task set
* Bind the user to the role
* Verify the user has limited access

We have to create a certificate credentials for a user because users are not API objects in Kubernetes and thus they require outside authentication such as OpenSSL certificates.
You have to generate it against the cluster certificate authority.

[TODO _Rewrite the following part in my words_]

Roles can then be used to configure an association of apiGroups, resources, and the verbs allowed to them.
The user can then be bound to a `role` limiting what and where they can work in the cluster.

#### Admission Control ####

Third and last step of accessing the API.

Admission controllers can inspect the content of the objects being created by the requests.
They can modify the content or validate it, and potentially deny the request.

Admission controllers (there are many that work together) have a specialization, examples:
`Initializers` allow dynamic modification of the request, `ResourceQuota` check for violations of any existing quota.

### Security Context ###

You add security constrains, called `security context` to [Pods](pod.md) and [containers](container.md).
This limit what the process inside containers can do (UID, capabilities, file system, ...).

Example:
```
apiVersion: v1
kind: Pod
metadata:
        name: nginx
spec:
        securityContext:
                runAsNonRoot: true
        containers:
        - image: nginx
          name: nginx
```
This Pod will never run as nginx needs root privileges.

Resource: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/

#### Pod Security Policies (PSP) ####

A Pod Security Policy is a rule at cluster level that govern what a [Pod](pod.md) can do.
In order to run in the cluster, a [Pod](pod.md) must match a PSP and it will execute with a security context that matches the policy plus some possible additional restrictions.

PSPs automate the enforcement of security contexts.

For Pod Security Policies to be enabled, you need to configure the [Admission Control](security#admission-controller) of the controller-manager to contain `PodSecurityPolicy`.
These policies make even more sense when coupled with the [[security#RBAC (Role Based Access Control)|RBAC]] configuration in your cluster.
This will allow you to finely tune what your users are allowed to run and what capabilities and low level privileges their containers will have.

Resources:
* PSP https://kubernetes.io/docs/concepts/policy/pod-security-policy/
* Walkthrough PSP + RBAC https://github.com/kubernetes/examples/tree/master/staging/podsecuritypolicy/rbac/

### Network Security Policies ###

By default all traffic is allowed, a Network Security Policy limit this.
They can be limited to a namespace, work on `podSelector` or `label`.
You can have multiple policies.
Not all network providers support the `NetworkPolicies` kind.

Example:
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
        name: ingress-egress-policy
        namespace: default
spec:
        podSelector:
                matchLabels:
                        role: db
        policyTypes:
        - Ingress
        - Egress
        ingress:
        - from:
                - ipBlock:
                        cidr: 172.17.0.0/16
                        except:
                                - 172.17.1.0/24
                - namespaceSelector:
                        matchLabels:
                                project: myproject
                - podSelector:
                        matchLabels:
                                role: frontend
                ports:
                - protocol: TCP
                  port: 6379
        egress:
        - to:
                - ipBlock:
                        cidr: 10.0.0.0/24
                ports:
                - protocol: TCP
                  port: 5978
```

These rules change the namespace for the following settings to be labeled project `myproject`.
The affected Pods also would need to match the label role `frontend`.
Finally TCP traffic on port 6379 would be allowed from these [Pods](pod.md).
 The egress rules have to settings, in this case the 10.0.0.0/24 range TCP traffic to port 5978.
 
The use of empty ingress or egress rules denies all of type of traffic for the included Pods, though not suggested.
Use another dedicated `NetworkPolicy` instead.

### Vulnerability list ###

See [Vulnerabilites](vulnerability.md).

### Random stuff for now ###

 * You can check access/permissions with
  ```
  kubectl aut can-i
  ```
  Examples:
  ```
  kubectl aut can-i create deployments
  kubectl aut can-i create deployments --as bob
  kubectl aut can-i create deployments --as bob --namespace developer
  ```
  The answer is a simple yes/no.
  Slide 108/458 for details.
  Or you can use `reconcile` for checking the authorization of objects creation from a file, no output means that you can.
