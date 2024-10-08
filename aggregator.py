import json

def extractFromMkit(resList=[]):
    """Extract the relevant fields from a Mkit output file and return them
    inside a list that will be used to create the final json
    """
    path = "results/results.json"
    with open(path, "r") as f:
        content = f.read()

    jsonP = json.loads(content)
    for result in jsonP["results"]:
        Name = result["title"]
        Category = result["category"]
        Severity = normalizeSeverityMkit(result["severity"])
        Description = result["description"]
        Remediation = result["remediation"]
        Evidence = result["validation"]
        if len(result["resources"]) > 0:
            for res in result["resources"]:
                element = {}
                element["Location"] = res["resource"]
                element["Name"] = Name
                element["Result"] = normalizeResultMkit(res["status"])
                element["Category"] = Category
                element["Severity"] = Severity
                element["Description"] = Description
                element["Remediation"] = Remediation
                element["Evidence"] = Evidence
                resList.append(element)
        else: # This shouldn't happen, just in case
            element = {}
            element["Location"] = result["category"]
            element["Name"] = Name
            element["Result"] = "N/A"
            element["Category"] = Category
            element["Severity"] = Severity
            element["Description"] = Description
            element["Remediation"] = Remediation
            element["Evidence"] = Evidence
            resList.append(element)

    resJson = json.dumps(resList)
    #print(resJson)
    return resList

def normalizeSeverityMkit(number):
    if number < 0.4:
        return "Low"
    elif number < 0.7:
        return "Medium"
    else:
        return "High"

def normalizeResultMkit(string):
    if string == "passed":
        return "Pass"
    else:
        return "Fail"

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
                element["Name"] = result["test_desc"] #Create a value?
                element["Result"] = "Pass" if result["status"] == "PASS" else "Fail"
                element["Category"] = test["desc"]
                element["Severity"] = normalizeSeverityCis(result["status"])
                element["Description"] = result["test_desc"]
                element["Remediation"] = result["remediation"]
                element["Evidence"] = result["audit"]
                resList.append(element)

    resJson = json.dumps(resList)
    #print(resJson)
    return resList

def normalizeSeverityCis(string):
    if string == "PASS" or string == "FAIL":
        return "High"
    else:
        return "Low"

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
        element["Result"] = "Fail"
        element["Category"] = result["category"]
        element["Severity"] = result["severity"].capitalize()
        element["Description"] = result["description"]
        element["Remediation"] = ""
        if isinstance(result["evidence"], list):
            result["evidence"].sort()
        element["Evidence"] = result["evidence"]
        resList.append(element)

    resJson = json.dumps(resList)
    #print(resJson)
    return resList

def extractFromKubesec(output, resList=[]):
    """Extract the relevant fields from the Kubesec output and return them
    inside a list that will be used to create the final json
    """
    for result in output:
        Location = "YAML - " + result["object"]
        if "critical" in result["scoring"]:
            for cr in result["scoring"]["critical"]:
                element = {}
                element["Location"] = Location
                element["Name"] = cr["selector"]
                element["Result"] = "Fail"
                element["Category"] = "Object definition in YAML file"
                element["Severity"] = "High"
                element["Description"] = cr["reason"]
                element["Remediation"] = ("Remove/set to false this selector in "
                    "the YAML definition")
                element["Evidence"] = ("This option is defined in the YAML "
                    "definition for " + result["object"])
                resList.append(element)
        if "advise" in result["scoring"]:
            for ad in result["scoring"]["advise"]:
                element = {}
                element["Location"] = Location
                element["Name"] = "Set " + ad["selector"]
                element["Result"] = "Fail"
                element["Category"] = "Object definition in YAML file"
                element["Severity"] = "Low"
                element["Description"] = ad["reason"]
                element["Remediation"] = ("Configure this selector in the YAML "
                    "definition of " + result["object"])
                element["Evidence"] = ("This option is missing from the YAML "
                    "definition for " + result["object"])
                resList.append(element)

    #resJson = json.dumps(resList)
    #print(resJson)
    return resList

def filterList(resList, field, condition):
    """Filter the result list using a field and a condition"""
    filteredList = []
    for res in resList:
        if res[field] == condition:
            filteredList.append(res)

    return filteredList

def integrateActive(hunterList, activeList, resList):
    """Compare elements from the vulnerability list generated by the simple
    hunter scan with the elements generated from the active one and add to the
    output list the additional findings from the activeList.

    The active list contains all the findings from the hunterList plus
    potentially some others found through active expolitation.
    """

    # if the length is the same, no additional findings have been found
    if len(hunterList) == len(activeList):
        return

    for res in activeList:
        duplicate = False
        for ac in hunterList:
            if res["Vulnerability"] == ac["Vulnerability"]:
                duplicate = True
                break
        if not duplicate:
            resList.append(res)

    return resList
