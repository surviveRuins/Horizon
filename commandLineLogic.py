import typer
import websocketConnection
import monitoredDomainsFileReader
from typing import Annotated

# Global variable because I don't want to pass this all the way trough the call stack, don't want to open the file for every new domain and don't want to overengineer right now
global_monitoredDomainsList = []
global_comboSquattingDetectionMethod = None
global_disable_progress_bar = 0

app = typer.Typer(no_args_is_help=True, add_completion=False, rich_markup_mode="markdown", pretty_exceptions_enable=False)

def initCLI():
    app()

combo_squatting_mode_help_message = """
The mode you want to operate the combosquatting detection in:
    \n\n- 1: flag any domain that has the string of the secondLevelDomain in it
    \n\n- 2: flag any domain that "secondLevelDomain-" or "-secondLevelDomain" in it. example-login.com,login-example.com will be flagged examplelogin.com will not be flagged for monitored domain example.com. This is basicially a combination of 3 and 4 and consists of a filter that is less strict
    \n\n- 3: flag any domain that "secondLevelDomain-" in it. example-login.com will be flagged examplelogin.com will not be flagged for monitored domain example.com
    \n\n- 4: flag any domain that has "-secondLevelDomain" in it. login-example-uber.com and login-examplefr.com will be flagged, example-login.com will not be flagged
    \n\n- 5: flag any domain that has "-secondLevelDomain.topLevelDomain" in it(meaning it has to end on our Fully qualified monitored domain. login-example.com will be flagged, login-example-uber.com won't be flagged
"""

@app.command()
def monitor(
        monitored_domains_list: str = typer.Option(None, "-dL", help="List of domains you want to monitor for domain squatting attemps"),
        monitored_domains: Annotated[list[str], typer.Option("-d", help="Domain you want to monitor for domain squatting attemps, can be specified multiple times")] = None,
        combo_squatting_mode: str = typer.Option(None, "-cM", help=combo_squatting_mode_help_message),
        disable_progress_bar: bool = typer.Option(None, "-nP", help="Disable display at the bottom that shows how many domains have been been streamed and checked for domain squatting")
):
    """
    Examples: 

    python3 horizon.py -dL monitoredDomains.txt -cM 2\n\n
    python3 horizon.py -dL monitoredDomains.txt -cM 3\n\n
    python3 horizon.py -d google.com -d paypal.com -d amazon.com -cM 5\n\n
    python3 horizon.py -d discord.com -cM 5\n
    python3 horizon.py -d discord.com -cM 5 -dP\n
    """
    global global_monitoredDomainsList # This is the way to grab a global variable in python, if you don't do this it will not be written to the global var defined above
    global global_comboSquattingDetectionMethod # This is the way to grab a global variable in python, if you don't do this it will not be written to the global var defined above

    if(disable_progress_bar):
        global global_disable_progress_bar
        global_disable_progress_bar = True

    if(monitored_domains_list):

        if(combo_squatting_mode):
            if(int(combo_squatting_mode) in [1,2,3,4,5]):
                global_comboSquattingDetectionMethod = combo_squatting_mode
            else:
                print("comboSquattingDetectionMethod -cM is not a valid value: 1,2,3,4 or 5")
                raise typer.Exit()


        global_monitoredDomainsList = monitoredDomainsFileReader.readFile(monitored_domains_list)
        websocketConnection.connect()

    elif(monitored_domains):

        if(combo_squatting_mode):
            if(int(combo_squatting_mode) in [1,2,3,4,5]):
                global_comboSquattingDetectionMethod = combo_squatting_mode
            else:
                print("comboSquattingDetectionMethod -cM is not a valid value: 1,2,3,4 or 5")
                raise typer.Exit()


        for monitored_domain in monitored_domains:
            global_monitoredDomainsList.append(monitored_domain) 
        websocketConnection.connect() 

    else:
        print("Invalid command provided. Please run again with --help")

def getMonitoredDomainsList():
    return global_monitoredDomainsList

def getComboSquattingDetectionMethod():
    return int(global_comboSquattingDetectionMethod)

def getDisableProgressBar():
    return global_disable_progress_bar
