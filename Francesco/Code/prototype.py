import argparse
import subprocess
import time
import requests
import threading
from os import path
#import psutil
#import docker
from kubernetes import client, config
import yaml
import json
from fetcher import *

def runTool(tool):
    """Decide which tool to run based on the argument"""
    if tool == "cis":
        runCisBench()
    elif tool == "kube-hunter":
        runHunter()
    elif tool == "kubesec":
        runKubesec()
    elif tool == "mkit":
        runMkit()
    elif tool == "custom":
        runMkit()
    else:
        print("Unexpected tool") #Shouldn't happen as there is the check before

def runCisBench():
    """Run aqua-bench (an implementation of the cis benchmark) as Pod
    """
    ns = "default"
    jobName = "kube-bench"
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()
    with open(path.join(path.dirname(__file__), "kubebatch-job.yaml")) as f:
        job = yaml.safe_load(f)
        resJob = batch_v1.create_namespaced_job(namespace=ns, body=job)

    jobStatus = batch_v1.read_namespaced_job_status(jobName, ns)

    time.sleep(3) #time waiting to start, how to remove the wait?
    while jobStatus.status.completion_time is None:
        time.sleep(1)
        jobStatus = batch_v1.read_namespaced_job_status(jobName, ns)

    uid = resJob.metadata.labels["controller-uid"]

    listEvents = core_v1.list_namespaced_event(ns,
    #field_selector="involvedObject.name=kube-bench")
    field_selector="involvedObject.uid={}".format(uid))
    podName = listEvents.items[0].message.split()[-1]

    """
    descriptionJob = core_v1.read_namespaced_event("kube-bench", ns)
    print(descriptionJob)
    """

    log = core_v1.read_namespaced_pod_log(name=podName, namespace=ns)
    print(log)
    return log

def runCisBenchDocker():
    """Run aqua-bench (an implementation of the cis benchmark) as Docker
    container
    """
    client = docker.from_env()
    kubectlPath = "/usr/bin/kubectl" #hardcoded, can be found with which
    volumesDict = {"/etc": {"bind": "/etc", "mode": "ro"},
            "/var": {"bind": "/var", "mode": "ro"},
            kubectlPath: {"bind": "/usr/local/mount-from-host/bin/kubectl",
                "mode": "ro"},
            "~/.kube": {"bind": "/.kube", "mode": "ro"}}
    log = client.containers.run("aquasec/kube-bench:latest", command="node",
            environment=["KUBECONFIG=/.kube/config"], pid_mode="host",
            tty=False, volumes=volumesDict)
    print(log)

"""
We have two options: run the job and then delete it or check for its existence
and rerun it when needed
"""
def runHunter():
    """Run kube-hunter
    Creates a Pod in the cluster used to run a Job that will scan the
    environment
    """
    ns = "default"
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()

    jobName = "kube-hunter-json"
    hunterJobFilename = "kube-hunter-job-json.yaml"

    with open(path.join(path.dirname(__file__), hunterJobFilename)) as f:
        hunterJob = yaml.safe_load(f)
        resJob = batch_v1.create_namespaced_job(namespace=ns, body=hunterJob)

    jobStatus = batch_v1.read_namespaced_job_status(jobName, ns)

    time.sleep(5) #time waiting to start, how to remove the wait?
    while jobStatus.status.completion_time is None:
        time.sleep(1)
        jobStatus = batch_v1.read_namespaced_job_status(jobName, ns)

    uid = resJob.metadata.labels["controller-uid"]

    listEvents = core_v1.list_namespaced_event(ns,
    field_selector="involvedObject.uid={}".format(uid))
    podName = listEvents.items[0].message.split()[-1]

    podLog = core_v1.read_namespaced_pod_log(name=podName, namespace=ns)

    jsonReport = extractJson(podLog)
    print(jsonReport)

    batch_v1.delete_namespaced_job(jobName, ns)

    return jsonReport

def extractJobNameJob(output):
    """Extract and return the Job name tied to kube-hunter from a kubectl
    describe jobs command output
    """
    lines = output.splitlines()
    podName = lines[-1].split()[-1] #check if right
    print(podName)
    return podName

def extractJobNamePods(output):
    """Extract and return the Job name tied to kube-hunter from a kubectl
    describe pods command output
    """
    lines = output.splitlines()
    podName = lines[0].split()[1] #check if right
    print(podName)
    return podName

def extractJson(log):
    """Extract and return the json output from the kube-hunter scan from the
    Pod logs"""
    start = log.find('{')
    if start == -1:
        return "" # add proper error mechanism
    json = log[start:]
    #print(json)
    return json

def runKubesec():
    """Run the Kubesec tool agains all yaml files in the cluster
    """
    files = complete_fetcher()

    # Execute kubesec scan on all files created
    total_scan = []
    for f in files:
        out = subprocess.run(["./kubesec", "scan", f], capture_output=True, text=True)
        total_scan.append(out.stdout)
        print(out.stdout)

def runMkit():
    """Run the mkit tool
    Returns the output in json format
    """
    # For the moment we assume that the tool has already been downloaded
    server = threading.Thread(target=serverRun)
    server.start()
    time.sleep(20) #hardcoded, find better way
    response = requests.get("http://localhost:8000/results.json")
    json = response.text
    print(json)
    return json

def serverRun():
    """Run the mkit server
    At the moment is just a simple call to make
    """
    subprocess.run(["make", "run-k8s"])

def runCustom():
    pass

# Command line parser logic
def parsing():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=["cis", "kube-hunter", "kubesec", "mkit",
        "custom"], help="select the tool to run")
    parser.add_argument("-v", "--verbosity", action="count", default=0,
        help="increase output verbosity")
    args = parser.parse_args()
    if args.verbosity >= 2:
        print("performing a check using {}".format(args.tool))
        print("More descriptive stuff to be determined")
        runTool(args.tool)
    elif args.verbosity >= 1:
        print("performing a check using {}".format(args.tool))
        runTool(args.tool)
    else:
        runTool(args.tool)

if __name__ == '__main__':
    parsing()
