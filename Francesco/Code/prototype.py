import argparse
import subprocess
import time
import os
from os import path
from contextlib import contextmanager
from pathlib import Path
from string import Template
from datetime import datetime

#import docker
from kubernetes import client, config
import yaml
import json

from fetcher import *
from aggregator import *

def runTool(tool, htmlFlag):
    """Decide which tool to run based on the argument"""
    outList = []
    if tool == "cis":
        out = runCisBench()
        outList = extractFromCis(out)
    elif tool == "kube-hunter":
        out = runHunter()
        outList = extractFromHunter(out)
    elif tool == "kubesec":
        out = runKubesec()
        outList = extractFromKubesec(out)
    elif tool == "mkit":
        runMkit()
        outList = extractFromMkit()
    elif tool == "custom":
        out = runCustom()
        outList = extractFromCustom()
    elif tool == "complete":
        # All sequencial, could be parallelized if we merge the lists at the
        # end
        hunterOut = runHunter()
        outList = extractFromHunter(hunterOut)
        kubesecOut = runKubesec()
        tmpList = extractFromKubesec(kubesecOut, outList)
        runMkit()
        outList = extractFromMkit(outList)
        cisOut = runCisBench()
        outList = extractFromCis(cisOut, outList)
        """
        customOut = runCustom()
        finalList = extractFromCustom(customOut, tmpList)
        """
    else:
        print("Unexpected tool") #Shouldn't happen as there is the check before
        return

    output(outList, htmlFlag)

def runCisBench():
    """Run aqua-bench (an implementation of the cis benchmark) as Pod
    """
    podLog = runToolAsJob("kube-bench", "kube-bench-job.yaml",
            "default")
    #print(podLog)
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
    #print(log)

def runHunter():
    """Run kube-hunter
    Creates a Pod in the cluster used to run a Job that will scan the
    environment
    """
    podLog = runToolAsJob("kube-hunter-json", "kube-hunter-job-json.yaml",
            "development")
    jsonReport = extractJson(podLog)
    #print(jsonReport)

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
        simpleExtract(out.stdout, total_scan)
    return total_scan

def simpleExtract(jsonString, outList=[]):
    jsonD = json.loads(jsonString)
    for el in jsonD:
        outList.append(el)

def runMkit():
    """Run the mkit tool
    Returns the output in json format
    """
    #Delete old results files
    old_results = Path("results/results.json") 
    old_results.unlink(missing_ok=True)
    old_results = Path("results/raw-results.json") 
    old_results.unlink(missing_ok=True)
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

def output(outputData, htmlFlag):
    if htmlFlag:
        createHtmlTemplate(outputData)
    else:
        #print(outputData)
        print(json.dumps(outputData))

def createHtml(outputData):
    begin = "<html><head></head><body>"
    end = "</body></html>"
    content = ""
    for res in outputData: #Change in Python string Template
        content += "<div class=\"" + res["Result"] + "\">"
        content += "<span class=\"title\">" + res["Location"] + " - " + res["Name"] + "</span>"
        content += "<br>"
        content += res["Severity"] + " - " + res["Result"]
        content += "<br>"
        content += "Description: " + res["Description"]
        content += "<br>"
        content += "Remediation: " + res["Remediation"]
        content += "<br>"
        content += "Evidence: " + res["Evidence"]
        content += "<br>"
        content += "</div>"
    html = begin + content + end

    with open(path.join(path.dirname(__file__), "report.html"), "w") as f:
        f.write(html)

def createHtmlTemplate(outputData):
    resultTemplate = ("<div class=\"$Result $Severity result \"><br>"
            "<span class=\"title\"> $Location - $Name </span><br>"
            "Category: $Category - Severity: $Severity - Result: $Result <br>"
            "Description: $Description <br>"
            "Remediation: $Remediation <br>"
            "Evidence: $Evidence <br>"
            "</div>")
    result = Template(resultTemplate)
    results = ""
    for res in outputData:
        results += result.substitute(res)

    page = Template("<html><head><style>$css</style></head><body>$title " + 
            "<div id=\"results\"> $results </div>" + 
            " </body></html>")

    with open(path.join(path.dirname(__file__), "report.css")) as f:
        css = f.read()

    scanTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    title = "<h1>Scan Report from {}</h1>".format(scanTime)
    html = page.substitute(css=css, title=title, results=results)

    with open(path.join(path.dirname(__file__), "reportT.html"), "w") as f:
        f.write(html)

# Command line parser logic
def parsing():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("tool", choices=["cis", "kube-hunter", "kubesec", "mkit",
        "custom", "complete"], help="select the tool to run")
    parser.add_argument("-v", "--verbosity", action="count", default=0,
        help="increase output verbosity")
    parser.add_argument("-o", "--output", choices=["json", "html"],
        default="json", help="set the output type, default to json")
    args = parser.parse_args()
    if args.verbosity >= 1:
        if args.tool == "complete":
            print("performing a complete check")
        else:
            print("performing a check using {}".format(args.tool))
    elif args.verbosity >= 2:
        print("The output method selected is {}".format(args.output))

    htmlFlag = True if args.output == "html" else False
    runTool(args.tool, htmlFlag)

if __name__ == '__main__':
    parsing()
