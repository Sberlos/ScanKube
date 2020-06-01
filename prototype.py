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
from decider import *

def runTool(tool, htmlFlag, onlyFailFlag, severity):
    """Decide which tool to run based on the argument"""
    outList = []
    filtered = False
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
        # save hunter list in a special way for comparing with active later
        hunterList = extractFromHunter(hunterOut)
        outList = hunterList
        kubesecOut = runKubesec()
        tmpList = extractFromKubesec(kubesecOut, outList)
        runMkit()
        outList = extractFromMkit(outList)
        cisOut = runCisBench()
        outList = extractFromCis(cisOut, outList)

        # sort for having a deterministic diff
        outList = sorted(outList, key=lambda k: k["Name"]) 
        """
        customOut = runCustom()
        finalList = extractFromCustom(customOut, tmpList)
        """
        decided = decide(outList)
        filtered = True
        if decided[0]:
            print("Starting active hunting")
            activeOut = runActive()
            #replace the old list or add? I think replace
            activeList = extractFromHunter(activeOut)
            integrateActive(hunterList, activeList, outList)
    else:
        print("Unexpected tool") #Shouldn't happen as there is the check before
        return

    # I would prefer to combine this conditions in only one iteration
    if onlyFailFlag:
        if not filtered:
            outList = filterList(outList, "Result", "Fail")
        else:
            # use the list computer in the decider
            outList = decided[1]

    if severity != "all":
        outList = filterList(outList, "Severity", severity.capitalize())

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
            "default")
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

def runActive():
    """Run kube-hunter in active mode
    Creates a Pod in the cluster used to run a Job that will try to expoloit
    vulnerabilities
    """
    podLog = runToolAsJob("kube-hunter-active", "kube-hunter-job-active.yaml",
            "default")
    jsonReport = extractJson(podLog)
    #print(jsonReport)

    return jsonReport


def output(outputData, htmlFlag):
    if htmlFlag:
        createHtmlTemplate(outputData)
    else:
        #print(outputData)
        print(json.dumps(outputData, indent=2)) #The indent should be a flag

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

    with open(path.join(path.dirname(__file__), "reportOld.html"), "w") as f:
        f.write(html)

def createHtmlTemplate(outputData):
    resultTemplate = ("<div class=\"$Result $Severity result \"><br>"
            "<div class=\"exT\"><span class=\"title\"> $Location <br>"
            "$Name </span></div>"
            "<div class=\"lineR\"><span class=\"desc\">Category:</span> $Category - "
            "<span class=\"desc\">Severity:</span> $Severity - "
            "<span class=\"desc\">Result:</span> $Result </div>"
            "<div class=\"lineR\"><span class=\"desc\">Description:</span> $Description </div>"
            "<div class=\"lineR\"><span class=\"desc\">Remediation:</span> $Remediation </div>"
            "<span class=\"desc\">Evidence:</span> $Evidence <br>"
            "</div>")
    result = Template(resultTemplate)

    passed = ""
    high = ""
    medium = ""
    low = ""
    for res in outputData:
        if res["Result"] == "Pass":
            passed += result.substitute(res)
        elif res["Severity"] == "High":
            high += result.substitute(res)
        elif res["Severity"] == "Medium":
            medium += result.substitute(res)
        elif res["Severity"] == "Low":
            low += result.substitute(res)

    resultsTemplate = (
        "<div id=\"high\" class=\"stitle\"><h3>High severity vulnerabilities</h3>$high </div>"
        "<div id=\"medium\" class=\"stitle\"><h3>Medium severity vulnerabilities</h3>$medium </div>"
        "<div id=\"low\" class=\"stitle\"><h3>Low severity vulnerabilities</h3>$low </div>"
        "<div id=\"passed\" class=\"stitle\"><h3>Passed tests</h3>$passed </div>")
    results = Template(resultsTemplate).substitute(high=high, medium=medium,
            low=low, passed=passed)

    menu = (
        "<div class=\"element\"><a href=#high>High severity</a></div>"
        "<div class=\"element\"><a href=#medium>Medium severity</a></div>"
        "<div class=\"element\"><a href=#low>Low severity</a></div>"
        "<div class=\"element\"><a href=#passed>Passed tests</a></div>")

    page = Template("<html><head><style>$css</style></head><body>$title " +
            "<div id=\"content\"><div id=\"menu\">$menu</div>" +
            "<div id=\"results\"> $results </div>" +
            "</div></body></html>")

    with open(path.join(path.dirname(__file__), "report.css")) as f:
        css = f.read()

    scanTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    title = "<h1>Scan Report from {}</h1>".format(scanTime)
    html = page.substitute(css=css, title=title, menu=menu, results=results)

    with open(path.join(path.dirname(__file__), "report.html"), "w") as f:
        f.write(html)

# Command line parser logic
def parsing():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("tool",
            choices=["cis", "kube-hunter", "kubesec", "mkit", "custom",
                "complete"],
            help="select the tool to run")
    parser.add_argument("-v", "--verbosity", action="count", default=0,
        help="increase output verbosity")
    parser.add_argument("-o", "--output", choices=["json", "html"],
        default="json", help="set the output type, default to json")
    parser.add_argument("-f", "--only-fail", action="store_true",
        help="return only failing tests")
    parser.add_argument("-s", "--set-severity", default="all",
        choices=["all", "high", "medium", "low"],
        help="show results with specified severity")
    args = parser.parse_args()
    if args.verbosity >= 1:
        if args.tool == "complete":
            print("performing a complete check")
        else:
            print("performing a check using {}".format(args.tool))
    elif args.verbosity >= 2:
        print("The output method selected is {}".format(args.output))

    htmlFlag = True if args.output == "html" else False
    #print(args)
    runTool(args.tool, htmlFlag, args.only_fail, args.set_severity)

if __name__ == '__main__':
    parsing()
