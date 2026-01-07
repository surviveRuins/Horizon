def readFile(fileName):

    monitoredDomainsList = []

    with open(fileName, "r") as file:
        for monitoredDomain in file:
            monitoredDomainsList.append(monitoredDomain)

    return monitoredDomainsList
