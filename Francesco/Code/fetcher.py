from kubernetes import client, config
from pathlib import Path

def complete_fetcher():
    """Fetch all relevant yaml files from the cluster
    At the moment kubesec supports only deployments, stateful sets, daemon sets
    and pods
    """
    namespaces_list = ["default"] #not used right now
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    apps_v1 = client.AppsV1Api()
    core_v1 = client.CoreV1Api()

    files = []

    """
    #Deployments
    all_deployments = apps_v1.list_deployment_for_all_namespaces()
    createYamlFiles(all_deployments, "deployment", files)

    #ReplicaSets
    all_replica_sets = apps_v1.list_replica_set_for_all_namespaces()
    createYamlFiles(all_replica_sets, "replicaSet", files)

    #StatefulSets
    all_stateful_sets = apps_v1.list_stateful_set_for_all_namespaces()
    createYamlFiles(all_stateful_sets, "statefulSet", files)

    #DaemonSets
    all_daemon_sets = apps_v1.list_daemon_set_for_all_namespaces()
    createYamlFiles(all_daemon_sets, "daemonSet", files)
    """

    #check if we need resources that are namespaced
    #for ns in namespaces_list:

    resources = [
            [apps_v1.list_deployment_for_all_namespaces, "deployment"],
            #[apps_v1.list_replica_set_for_all_namespaces, "replicaSet"],
            [apps_v1.list_stateful_set_for_all_namespaces, "statefulSet"],
            [apps_v1.list_daemon_set_for_all_namespaces, "daemonSet"],
            #[batch_v1.list_job_for_all_namespaces, "job"],
            #[core_v1.list_pod_for_all_namespaces, "pod"],
            ]

    # extract the yaml files for every resource specified above
    for r in resources:
        listObjects(r[0], r[1], files)

    return files

def listObjects(function, name, files):
    """List all objects using the function for their type and create a yaml
    file with the spec
    """
    res = function() #query the API for the objects
    createYamlFiles(res, name, files)

def createYamlFiles(response, name, files):
    """Create yaml spec files from the object in the response of the API
    """
    directory = "extracted_objects"
    Path(directory).mkdir(exist_ok=True)
    c = 0
    for i in response.items:
        if "kubectl.kubernetes.io/last-applied-configuration" in i.metadata.annotations:
            filename = "{}_{}.yaml".format(name, c)
            path = "{}/{}".format(directory, filename)
            with open(path, "w") as f:
                f.write(i.metadata.annotations[
                    "kubectl.kubernetes.io/last-applied-configuration"])
            files.append(path)
            c += 1

