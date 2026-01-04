import sys
from rapidfuzz.distance import DamerauLevenshtein
import base64

# This is the handler for the domain stream coming in, We get raw domains with wildcards removed as a string.
# Everytime the streamIngest function is called 1 new domain was sent to the websocket client by my server.
# I can't really believe it either but all the processing doesn't seem to slow the websocket down enough to fall behind the newest state.
# I did some testing by printing them all here and running wscat on a seperate maschine but it genuinly seems to work perfectly.

monitoredDomainsList = []
counter = 0
comboSwappingDetectionTreshold = 4; # 1: flag any domain that has the string of the secondLevelDomain in it
                                    # 2: flag any domain that "secondLevelDomain-" (or _) in it. example-login.com will be flagged examplelogin.com will not be flagged for monitored domain example.com
                                    # 3: flag any domain that has "-secondLevelDomain" (or _) in it. login-example-uber.com and login-examplefr.com will be flagged, example-login.com will not be flagged
                                    # 4: flag any domain that has "-secondLevelDomain.topLevelDomain" (or _) in it(meaning it has to end on our Fully qualified monitored domain.
                                    #    login-example.com will be flagged, login-example-uber.com will not be flagged

with open(sys.argv[1], "r") as file:
    for monitoredDomain in file:
        monitoredDomainsList.append(monitoredDomain)

class Colors:
    RED = '\033[31m'      # Errors / [!]
    GREEN = '\033[32m'    # Success / [+]
    YELLOW = '\033[33m'   # Warning / [*]
    BLUE = '\033[94m'     # Info / [?]
    RESET = '\033[0m'     # Reset to default



def color(pSecondLevelDomain, pColor):
    return f"{getattr(Colors, pColor)}{pSecondLevelDomain}{Colors.RESET}"

def detectComboSquatting(monitoredDomain, domain):
    # Assumption for our list of monitored domains from the file given by the user in sys.argv[1]: One domain in format main.tld per line: 
    # That means we need to seperate the `main` part as that is the only relevant thing for comboswapping: paypal.com --> paypal --> now we can detect if the streamIngest() data contains paypal as a signal for comboswapping
    # In paypal.com the `.com` is called TLD(Top Level Domain) and the `paypal` is called SLD(Second Level Domain)
    
    secondLevelDomain = monitoredDomain.split(".")[0]

    match(comboSwappingDetectionTreshold):
        case 1:
            if secondLevelDomain in domain:
                print("Combosquatting: ", end='')
                print(domain.replace(secondLevelDomain, color(secondLevelDomain, 'RED')))
        case 2:
            if f"{secondLevelDomain}-" in domain:
                print("Combosquatting: ", end='')
                print(domain.replace(f"{secondLevelDomain}-", color(f"{secondLevelDomain}-", 'RED')))
        case 3:
            if f"-{secondLevelDomain}" in domain:
                print("Combosquatting: ", end='')
                print(domain.replace(f"-{secondLevelDomain}", color(f"-{secondLevelDomain}", 'RED')))
        case 4:
            if f"-{monitoredDomain}" in domain:
                print("Combosquatting: ", end='')
                print(domain.replace(f"-{monitoredDomain}", color(f"-{monitoredDomain}", 'RED')))

def detectTLDSquatting(monitoredDomain, domain):

    # This will detect TLD Squatting attempts or show live domains that are already TLD squatting your monitored domain. 
    # That means if a domain exists(and subdomain is added and shows up in CT log) or is freshly registered you will be alerted if it looks like a TLD squatting attempt
    # Example: example.com ----> example.team is registered and HR-impersonating emails are sent.

    monitoredSecondLevelDomain = monitoredDomain.split(".")[-2]  # Get last element of the domainArray which by definition will always be the TLD(Top Level Domain) (assuming domains are provided as main.com and not main.com. or .com.main)
    secondLevelDomain = domain.split(".")[-2]  # Get last element of the domainArray which by definition will always be the TLD(Top Level Domain) (assuming domains are provided as main.com and not main.com. or .com.main)

    monitoredTopLevelDomain = monitoredDomain.split(".")[-1]     # Get last element of the domainArray which by definition will always be the TLD(Top Level Domain) (assuming domains are provided as main.com and not main.com. or .com.main)
    topLevelDomain = domain.split(".")[-1]  # Get last element of the domainArray which by definition will always be the TLD(Top Level Domain) (assuming domains are provided as main.com and not main.com. or .com.main)


    if(secondLevelDomain == monitoredSecondLevelDomain):
        if(topLevelDomain != monitoredTopLevelDomain):
            print("TLDSquatting: ", end='')
            secondAndTopLevelDomain = secondLevelDomain + "." + topLevelDomain
            print(domain.replace(secondAndTopLevelDomain, color(secondAndTopLevelDomain, 'RED')))

def detectTypoSquatting(monitoredDomain, domain):
    damerauLevenshteinSimilarity = DamerauLevenshtein.normalized_similarity(domain, monitoredDomain)   # This is calculated by using the distance, normalizing it to a range of [0,1] and then
                                                                                                           # doing `1 - normalized_distance`. So for a damerauLevenshteinDistance of 4: 4 --> 0.4 --> 1 - 0.4 = 0.6 Similarity
    if(damerauLevenshteinSimilarity >= 0.5):
        print(color(domain, 'RED'))

def detectSubdomainSquatting(monitoredDomain, domain):

    # This will detect subdomain squatting. In Subdomain Squatting an attacker registers a domain like amazon.google.attacker.org trying to phish
    # victims by impersonating amazon or google, when in reality it is just a subdomain of an arbitiary domain the Attacker controlls

    domainList = domain.split(".")

    monitoredSecondLevelDomain = monitoredDomain.split(".")[-2]
    secondLevelDomain = domain.split(".")[-2]

    if monitoredSecondLevelDomain in domainList and monitoredSecondLevelDomain != secondLevelDomain:
        print("SubdomainSquatting: ", end='')
        print(domain.replace(monitoredSecondLevelDomain, color(monitoredSecondLevelDomain, 'RED')))


def streamIngest(domain):
    for monitoredDomain in monitoredDomainsList:
        monitoredDomain = monitoredDomain.split("\n")[0] # The string includes a \n at the end which we need to remove for proper parsing later
        detectComboSquatting(monitoredDomain, domain)
        detectTLDSquatting(monitoredDomain, domain)
        # detectTypoSquatting(monitoredDomain, domain)     # This does produce too many false positves right now, ai detection?
        detectSubdomainSquatting(monitoredDomain, domain)

    
