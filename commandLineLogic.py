import typer
import websocketConnection
import monitoredDomainsFileReader
from typing import Annotated

# Global variable because I don't want to pass this all the way trough the call stack, don't want to open the file for every new domain and don't want to overengineer right now
global_monitoredDomainsList = []
global_levelSquattingDetectionMethod = None
global_disable_progress_bar = 0
global_damerauLevensheinSimilarityTreshhold = 0.7
global_cerstream_url = "ws://138.199.224.29:8080/domains-only"  # Use my server as default as it is already running and works out of the box

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

level_squatting_mode_help_message = """
The mode you want to operate the levelsquatting detection in:
    \n\n- 1: flag any domain that has the string of the secondLevelDomain in it
    \n\n- 2: flag any domain that "secondLevelDomain-" or "-secondLevelDomain" in it. example-login.com,login-example.com will be flagged examplelogin.com will not be flagged for monitored domain example.com. This is basicially a combination of 3 and 4 and consists of a filter that is less strict
    \n\n- 3: flag any domain that "secondLevelDomain-" in it. example-login.com will be flagged examplelogin.com will not be flagged for monitored domain example.com
    \n\n- 4: flag any domain that has "-secondLevelDomain" in it. login-example-uber.com and login-examplefr.com will be flagged, example-login.com will not be flagged
    \n\n- 5: flag any domain that has "-secondLevelDomain.topLevelDomain" in it(meaning it has to end on our Fully qualified monitored domain. login-example.com will be flagged, login-example-uber.com won't be flagged
"""

damerau_levenshtein_similarity_treshhold_message = """
    How similar the domain needs to be to be detected as typosquatting. Input from 0.0 - 1.0. Uses Damerau Levenshtein Distance normalized to 0.0-1.0
"""

@app.command(epilog = usageExampleString)
def monitor(
        monitored_domains_list: str = typer.Option(None, "--domain-list", "-l", help="List of domains you want to monitor for domain squatting attempts"),
        monitored_domains: Annotated[list[str], typer.Option("--domain", "-d", help="Domain you want to monitor for domain squatting attemps, can be specified multiple times")] = None,
        disable_progress_bar: bool = typer.Option(False,"--no-progress", "-n", help="Disable display at the bottom that shows how many domains have been been streamed and checked for domain squatting"),
        damerau_levenshein_similarity_treshhold: str = typer.Option(None, "--similarity-treshhold", "-t", help=damerau_levenshtein_similarity_treshhold_message),
        certstream_url: str = typer.Option(None, "--certstream-url", "-u", help="The URL of the cerstream server that exposes a websocket"),
        level_squatting_mode: str = typer.Option(None,"--level-mode", "-m", help=level_squatting_mode_help_message),
):
    global global_monitoredDomainsList # This is the way to grab a global variable in python, if you don't do this it will not be written to the global var defined above
    global global_levelSquattingDetectionMethod # This is the way to grab a global variable in python, if you don't do this it will not be written to the global var defined above

    if(disable_progress_bar):
        global global_disable_progress_bar
        global_disable_progress_bar = True

    if(damerau_levenshein_similarity_treshhold):
        global global_damerauLevensheinSimilarityTreshhold
        global_damerauLevensheinSimilarityTreshhold = damerau_levenshein_similarity_treshhold

    if(certstream_url):
        global global_cerstream_url
        global_cerstream_url = certstream_url

    if(monitored_domains_list):

        if(level_squatting_mode):
            if(int(level_squatting_mode) in [1,2,3,4,5]):
                global_levelSquattingDetectionMethod = level_squatting_mode
            else:
                print("levelSquattingDetectionMethod -cM is not a valid value: 1,2,3,4 or 5")
                raise typer.Exit()


        global_monitoredDomainsList = monitoredDomainsFileReader.readFile(monitored_domains_list)
        websocketConnection.connect()

    elif(monitored_domains):

        if(level_squatting_mode):
            if(int(level_squatting_mode) in [1,2,3,4,5]):
                global_levelSquattingDetectionMethod = level_squatting_mode
            else:
                print("levelSquattingDetectionMethod -cM is not a valid value: 1,2,3,4 or 5")
                raise typer.Exit()


        for monitored_domain in monitored_domains:
            global_monitoredDomainsList.append(monitored_domain) 
        websocketConnection.connect() 

    else:
        print("Invalid command provided. Please run again with --help")

def getMonitoredDomainsList():
    return global_monitoredDomainsList

def getLevelSquattingDetectionMethod():
    return int(global_levelSquattingDetectionMethod)

def getDisableProgressBar():
    return global_disable_progress_bar

def getDamerauLevensheinSimilarityTreshhold():
    return float(global_damerauLevensheinSimilarityTreshhold)

def getCertstreamURL():
    return global_cerstream_url
