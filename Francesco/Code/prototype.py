import argparse
import subprocess
import time
import os
from os import path
from contextlib import contextmanager

#import docker
from kubernetes import client, config
import yaml
import json

from fetcher import *
from aggregator import *

def runTool(tool):
    """Decide which tool to run based on the argument"""
    if tool == "cis":
        out = runCisBench()
        extractFromCis(out)
    elif tool == "kube-hunter":
        hunterOut = runHunter()
        hunterList = extractFromHunter(hunterOut)
    elif tool == "kubesec":
        runKubesec()
    elif tool == "mkit":
        runMkit()
        mkitList = extractFromMkit()
    elif tool == "custom":
        runCustom()
    elif tool == "complete":
        # All sequencial, could be parallelized if we merge the lists at the
        # end
        hunterOut = runHunter()
        hunterList = extractFromHunter(hunterOut)
        kubesecOut = runKubesec()
        tmpList = extractFromKubesec(kubesecOut, hunterList)
        mkitOut = runMkit()
        tmpList = extractFromMkit(mkitOut, tmpList)
        customOut = runCustom()
        finalList = extractFromCustom(customOut, tmpList)
        output(finalList)
    else:
        print("Unexpected tool") #Shouldn't happen as there is the check before

def runCisBench():
    """Run aqua-bench (an implementation of the cis benchmark) as Pod
    """
    podLog = runToolAsJob("kube-bench", "kube-bench-job.yaml",
            "default")
    print(podLog)
    return podLog

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

def runHunter():
    """Run kube-hunter
    Creates a Pod in the cluster used to run a Job that will scan the
    environment
    """
    podLog = runToolAsJob("kube-hunter-json", "kube-hunter-job-json.yaml",
            "development")
    jsonReport = extractJson(podLog)
    print(jsonReport)

    return jsonReport

def extractJson(log):
    """Extract and return the json output from the kube-hunter scan from the
    Pod logs"""
    start = log.find('{')
    if start == -1:
        return "" # add proper error mechanism
    json = log[start:]
    return json

def runToolAsJob(jobName, jobFilename, namespace):
    """Helper function that runs a job in a pod given the name of the job
    the name of the spec file and the namespace to run.
    It extracts the log and return it to the parent, then remove the job and
    the pod.
    """
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    core_v1 = client.CoreV1Api()

    with open(path.join(path.dirname(__file__), jobFilename)) as f:
        loadedJob = yaml.safe_load(f)
        resJob = batch_v1.create_namespaced_job(namespace=namespace, body=loadedJob)

    jobStatus = batch_v1.read_namespaced_job_status(jobName, namespace)

    time.sleep(5) #time waiting to start, how to remove the wait?
    while jobStatus.status.completion_time is None:
        time.sleep(1)
        jobStatus = batch_v1.read_namespaced_job_status(jobName, namespace)

    uid = resJob.metadata.labels["controller-uid"]

    listEvents = core_v1.list_namespaced_event(namespace,
    field_selector="involvedObject.uid={}".format(uid))
    podName = listEvents.items[0].message.split()[-1]

    podLog = core_v1.read_namespaced_pod_log(name=podName, namespace=namespace)

    batch_v1.delete_namespaced_job(jobName, namespace)
    core_v1.delete_namespaced_pod(podName, namespace)

    return podLog

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
    with cd("mkitMod"):
        subprocess.run(["make", "build"])
        subprocess.run(["make", "run-k8s"])

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

def runCustom():
    pass

# Command line parser logic
def parsing():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=["cis", "kube-hunter", "kubesec", "mkit",
        "custom", "complete"], help="select the tool to run")
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
