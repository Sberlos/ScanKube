import argparse
import subprocess
import time
import requests
import threading
#import psutil

def runTool(tool):
    if tool == "cis":
        runCis()
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

def runCis():
    pass

"""
We have two options: run the job and then delete it or check for its existence
and rerun it when needed
"""
def runHunter():
    # Basic invokation of kubectl, we could find better ways using the API
    subprocess.run(["kubectl", "create", "-f", "kube-hunter-job-json.yaml"])
    time.sleep(5) #Seems to be needed, I have to check

    """
    describeOutP = subprocess.run(["kubectl", "describe", "job",
        "kube-hunter-json-test"], capture_output=True, text=True)
    """
    describeOutP = subprocess.run(["kubectl", "describe", "pods",
        "kube-hunter-json-test"], capture_output=True, text=True)
    describeOut = describeOutP.stdout #not handling errors for now
    podName = extractJobNamePods(describeOut)

    time.sleep(25) #hardcoded, ideally we should keep describing/checking until completed
    podLogP = subprocess.run(["kubectl", "logs", podName], capture_output=True,
            text=True)
    podLog = podLogP.stdout #not handling errors for now

    jsonReport = extractJson(podLog)
    return jsonReport

def extractJobNameJob(output):
    lines = output.splitlines()
    podName = lines[-1].split()[-1] #check if right
    print(podName)
    return podName

def extractJobNamePods(output):
    lines = output.splitlines()
    podName = lines[0].split()[1] #check if right
    print(podName)
    return podName

def extractJson(log):
    start = log.find('{')
    if start == -1:
        return "" # add proper error mechanism
    json = log[start:]
    print(json)
    return json

def runKubesec():
    pass

def runMkit():
    # For the moment we assume that the tool has already been downloaded
    server = threading.Thread(target=serverRun)
    server.start()
    time.sleep(20) #hardcoded, find better way
    response = requests.get("http://localhost:8000/results.json")
    json = response.text
    print(json)
    return json

def serverRun():
    subprocess.run(["make", "run-k8s"])
def runCustom():
    pass

# Command line parser logic
def parsing():
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
