import json

def extractFromMkit(resList=[]):
    """Extract the relevant fields from a Mkit output file and return them
    inside a list that will be used to create the final json
    """
    path = "results/results.json"
    with open(path, "r") as f:
        content = f.read()

    # TODO this is wrong as we have multiple resources for the same vuln
    jsonP = json.loads(content)
    for result in jsonP["results"]:
        element = {}
        element["Location"] = result["category"]
        element["Name"] = result["title"]
        element["Category"] = result["category"]
        element["Severity"] = result["severity"]
        element["Description"] = result["description"]
        element["Remediation"] = result["remediation"]
        element["Evidence"] = result["validation"]
        resList.append(element)

    """
    resJson = json.dumps(resList)
    print(resJson)
    """
    return resList

def extractFromCis(output, resList=[]):
    """Extract the relevant fields from kube-bench output and return them
    inside a list that will be used to create the final json
    """

    jsonList = divideCisJson(output)
    for j in jsonList:
        jsonP = json.loads(j)
        for test in jsonP["tests"]:
            for result in test["results"]:
                element = {}
                element["Location"] = "K8s"
                element["Name"] = result["test_desc"]
                element["Category"] = test["desc"]
                element["Severity"] = result["status"]
                element["Description"] = result["test_desc"]
                element["Remediation"] = result["remediation"]
                element["Evidence"] = result["audit"]
                resList.append(element)

    resJson = json.dumps(resList)
    print(resJson)
    return resList

def divideCisJson(output):
    jsonList = output.split("\n")[:-1]

    return jsonList

def extractFromHunter(output, resList=[]):
    """Extract the relevant fields from the Hunter output and return them
    inside a list that will be used to create the final json
    """

    jsonP = json.loads(output)
    for result in jsonP["vulnerabilities"]:
        element = {}
        element["Location"] = result["location"]
        element["Name"] = result["vulnerability"]
        element["Category"] = result["category"]
        element["Severity"] = result["severity"]
        element["Description"] = result["description"]
        element["Remediation"] = ""
        element["Evidence"] = result["evidence"]
        resList.append(element)

    resJson = json.dumps(resList)
    print(resJson)
    return resList
