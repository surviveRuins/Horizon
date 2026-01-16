import typer
import websocketConnection
import monitoredDomainsFileReader
from typing import Annotated

# Global variable because I don't want to pass this all the way trough the call stack, don't want to open the file for every new domain and don't want to overengineer right now
global_monitoredDomainsList = []
global_comboSquattingDetectionMethod = None
global_disable_progress_bar = 0
global_damerauLevensheinSimilarityTreshhold = 0.7
global_cerstream_url = "ws://138.199.224.29:8080/domains-only"  # Use my server as default as it is already running and works out of the box
global_excludedDetectionModeList = []

# Not sure why this is how the formatting has to be to produce newlines...
usageExampleString = """
    **Examples:**\n\n 

    python3 horizon.py -u ws://138.199.224.29:8080/domains-only -l monitoredDomains.txt -m 2\n\n

    python3 horizon.py -u ws://138.199.224.29:8080/domains-only -l monitoredDomains.txt -m 3\n\n

    python3 horizon.py -u ws://138.199.224.29:8080/domains-only -d google.com -d paypal.com -d amazon.com -m 5\n\n

    python3 horizon.py -u ws://138.199.224.29:8080/domains-only -d discord.com -m 5\n\n

    python3 horizon.py -u ws://138.199.224.29:8080/domains-only -d discord.com -m 5 -n\n\n

    python3 horizon.py -u ws://138.199.224.29:8080/domains-only -d discord.com -m 5 -t 0.7\n\n
"""

app = typer.Typer(no_args_is_help=True, add_completion=False, rich_markup_mode="markdown", pretty_exceptions_enable=False)

def initCLI():
    app()

combo_squatting_mode_help_message = """
The mode you want to operate the combosquatting detection in:
    \n\n- 1: flag any domain that has the string of the secondcomboDomain in it
    \n\n- 2: flag any domain that "secondcomboDomain-" or "-secondcomboDomain" in it. example-login.com,login-example.com will be flagged examplelogin.com will not be flagged for monitored domain example.com. This is basicially a combination of 3 and 4 and consists of a filter that is less strict
    \n\n- 3: flag any domain that "secondcomboDomain-" in it. example-login.com will be flagged examplelogin.com will not be flagged for monitored domain example.com
    \n\n- 4: flag any domain that has "-secondcomboDomain" in it. login-example-uber.com and login-examplefr.com will be flagged, example-login.com will not be flagged
    \n\n- 5: flag any domain that has "-secondcomboDomain.topcomboDomain" in it(meaning it has to end on our Fully qualified monitored domain. login-example.com will be flagged, login-example-uber.com won't be flagged
"""

damerau_levenshtein_similarity_treshhold_message = """
    How similar the domain needs to be to be detected as typosquatting. Input from 0.0 - 1.0. Uses Damerau Levenshtein Distance normalized to 0.0-1.0
"""

exclude_detection_modes_help_message = """
    Squatting method you don't want to be used, can be specified multiple times. Good for filtering false positives
    or if you only want to use one detection method(to do this, exclude every detection method but the one you want)
"""

@app.command(epilog = usageExampleString)
def monitor(
        monitored_domains_list: str = typer.Option(None, "--domain-list", "-l", help="Path to file that contains List of domains you want to monitor for domain squatting attempts"),
        monitored_domains: Annotated[list[str], typer.Option("--domain", "-d", help="Domain you want to monitor for domain squatting attemps, can be specified multiple times")] = None,
        disable_progress_bar: bool = typer.Option(False,"--no-progress", "-n", help="Disable display at the bottom that shows how many domains have been been streamed and checked for domain squatting"),
        damerau_levenshein_similarity_treshhold: str = typer.Option(None, "--similarity-treshhold", "-t", help=damerau_levenshtein_similarity_treshhold_message),
        certstream_url: str = typer.Option(None, "--certstream-url", "-u", help="The URL of the cerstream server that exposes a websocket"),
        exclude_detection_modes: Annotated[list[str], typer.Option("--exclude", "-x", help=exclude_detection_modes_help_message)] = None,
        combo_squatting_mode: str = typer.Option(None,"--combo-mode", "-m", help=combo_squatting_mode_help_message),
):
    global global_monitoredDomainsList # This is the way to grab a global variable in python, if you don't do this it will not be written to the global var defined above
    global global_comboSquattingDetectionMethod # This is the way to grab a global variable in python, if you don't do this it will not be written to the global var defined above

    if(disable_progress_bar):
        global global_disable_progress_bar
        global_disable_progress_bar = True

    if(damerau_levenshein_similarity_treshhold):
        global global_damerauLevensheinSimilarityTreshhold
        global_damerauLevensheinSimilarityTreshhold = damerau_levenshein_similarity_treshhold

    if(certstream_url):
        global global_cerstream_url
        global_cerstream_url = certstream_url

    if(exclude_detection_modes):

        global global_excludedDetectionModeList

        for exclude_detection_mode in exclude_detection_modes:
            match(exclude_detection_mode):
                case "combo":
                    global_excludedDetectionModeList.append("combo") 
                case "tld":
                    global_excludedDetectionModeList.append("tld") 
                case "typo":
                    global_excludedDetectionModeList.append("typo") 
                case "level":
                    global_excludedDetectionModeList.append("level") 
            

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

def getDamerauLevensheinSimilarityTreshhold():
    return float(global_damerauLevensheinSimilarityTreshhold)

def getCertstreamURL():
    return global_cerstream_url

def getExcludedDetectionModeList():
    global_excludedDetectionModeList
    return global_excludedDetectionModeList
