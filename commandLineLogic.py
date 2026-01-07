import typer
import websocketConnection
import monitoredDomainsFileReader


# Global variable because I don't want to pass this all the way trough the call stack, don't want to open the file for every new domain and don't want to overengineer right now
global_monitoredDomainsList = []


def initCLI():
    typer.run(parseArgsAndOptions)

def parseArgsAndOptions(monitored_domains_list: str):
    global global_monitoredDomainsList # This is the way to grab a global variable in python, if you don't do this it will not be written to the global var defined above
    global_monitoredDomainsList = monitoredDomainsFileReader.readFile(monitored_domains_list)
    websocketConnection.connect()

def getMonitoredDomainsList():
    return global_monitoredDomainsList
