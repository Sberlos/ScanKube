from aggregator import filterList

def decide(output):
    """Takes the output of the first analysis and decide wheater to propose to
    the user to run the destructive tools
    """
    onlyFailList = filterList(output, "Result", "Fail")
    totalCount = len(onlyFailList)
    highCount = 0
    for res in onlyFailList:
        if res["Severity"] == "High":
            highCount += 1

    """
    print(highCount)
    print(totalCount)
    """
    choice = False
    if highCount / totalCount < 0.2:
        choice = proposeActive()
    return (choice, onlyFailList)

def proposeActive():
    print(("We detected the conditions for an active scan for "
           "vulnerabilities would you like to proceed?"))
    print("BE CAREFUL! AN ACTIVE HUNTING COULD BE HARMFUL TO YOUR CLUSTER!")
    response = input("Do the active hunting?[y/N]")
    response = response.lower() #transfrom to lowercase for reducing tests

    if response == "y" or response == "yes":
        print("You selected active hunting")
        return True

    return False
