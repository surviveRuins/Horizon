import typer
import websocketConnection
import monitoredDomainsFileReader


# Global variable because I don't want to pass this all the way trough the call stack, don't want to open the file for every new domain and don't want to overengineer right now
global_monitoredDomainsList = []

def initCLI():
    typer.run(parseFlagsAndArgs)

def parseFlagsAndArgs(monitored_domains_list: str = "", monitored_domain: str = ""):
    global global_monitoredDomainsList # This is the way to grab a global variable in python, if you don't do this it will not be written to the global var defined above

    if(monitored_domains_list):
        global_monitoredDomainsList = monitoredDomainsFileReader.readFile(monitored_domains_list)
        websocketConnection.connect()
    print("Invalid command provided. Please run again with --help")

def getMonitoredDomainsList():
    return global_monitoredDomainsList
