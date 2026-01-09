import typer
from horizon import websocketConnection
from horizon import monitoredDomainsFileReader


# Global variable because I don't want to pass this all the way trough the call stack, don't want to open the file for every new domain and don't want to overengineer right now
global_monitoredDomainsList = []

app = typer.Typer(no_args_is_help=True, add_completion=False)

def initCLI():
    app()

abc = "hey\n\nho"
combo_squatting_mode_help_message = "The mode you want to operate the combosquatting detection in:\n\n1: a\n\n2: b\n\n3:c\n\n4:d\n\n5:e"

@app.command()
def monitor(
        monitored_domains_list: str = typer.Option(None, "-dL", help="List of domains you want to monitor for domain squatting attemps"),
        #monitored_domains: str = typer.Option(None, "-d", help="Domain you want to monitor for domain squatting attemps, can be specified multiple times"),
        monitored_domains: str = typer.Option(None, "-d", help="Domain you want to monitor for domain squatting attemps, can be specified multiple times"),
        combo_squatting_mode: str = typer.Option(None, "-cM", help=combo_squatting_mode_help_message),
):
    global global_monitoredDomainsList # This is the way to grab a global variable in python, if you don't do this it will not be written to the global var defined above

    if(monitored_domains_list):
        global_monitoredDomainsList = monitoredDomainsFileReader.readFile(monitored_domains_list)
        websocketConnection.connect()

    print("Invalid command provided. Please run again with --help")

def getMonitoredDomainsList():
    return global_monitoredDomainsList
