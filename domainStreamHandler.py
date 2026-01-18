import sys
from rapidfuzz.distance import DamerauLevenshtein
import math
import commandLineLogic

# This is the handler for the domain stream coming in, We get raw domains with wildcards removed as a string.
# Everytime the streamIngest function is called 1 new domain was sent to the websocket client by my server.
# I can't really believe it either but all the processing doesn't seem to slow the websocket down enough to fall behind the newest state.
# I did some testing by printing them all here and running wscat on a seperate maschine but it genuinly seems to work perfectly.

#TODO: tld squatting detection doesn't work properly for multiple -d as other already known TLDs aren't registered

secondAndTopLevelDomainVisitedList = []

monitoredDomainsList = []
comboSquattingDetectionTreshold = 1;# 1: flag any domain that has the string of the secondLevelDomain in it
                                    # 2: flag any domain that "secondLevelDomain-" or "-secondLevelDomain" in it. example-login.com,login-example.com will be flagged examplelogin.com will
                                    #    not be flagged for monitored domain example.com. This is basicially a combination of 3 and 4 and consists of a filter that is less strict
                                    # 3: flag any domain that "secondLevelDomain-" in it. example-login.com will be flagged examplelogin.com will not be flagged for monitored domain example.com
                                    # 4: flag any domain that has "-secondLevelDomain" in it. login-example-uber.com and login-examplefr.com will be flagged, example-login.com will not be flagged
                                    # 5: flag any domain that has "-secondLevelDomain.topLevelDomain" in it(meaning it has to end on our Fully qualified monitored domain.
                                    #    login-example.com will be flagged, login-example-uber.com will not be flagged
class Colors:
    RED = '\033[31m'      # Errors / [!]
    GREEN = '\033[32m'    # Success / [+]
    YELLOW = '\033[33m'   # Warning / [*]
    BLUE = '\033[94m'     # Info / [?]
    RESET = '\033[0m'     # Reset to default


    

def color(pSecondLevelDomain, pColor):
    return f"{getattr(Colors, pColor)}{pSecondLevelDomain}{Colors.RESET}"

def detectComboSquatting(monitoredDomain, domain, domainStringBlacklist):
    # Assumption for our list of monitored domains from the file given by the user in sys.argv[1]: One domain in format main.tld per line: 
    # That means we need to seperate the `main` part as that is the only relevant thing for comboSquatting: paypal.com --> paypal --> now we can detect if the streamIngest() data contains paypal as a signal for comboSquatting
    # In paypal.com the `.com` is called TLD(Top Level Domain) and the `paypal` is called SLD(Second Level Domain)

    secondLevelDomain = monitoredDomain.split(".")[0]

    match(comboSquattingDetectionTreshold):
        case 1:
            if secondLevelDomain in domain:
                if not any(blacklistedString in domain for blacklistedString in domainStringBlacklist):
                    print("ComboSquatting: ", end='')
                    print(domain.replace(secondLevelDomain, color(secondLevelDomain, 'RED')))
        case 2:
            if f"{secondLevelDomain}-" in domain:
                if not any(blacklistedString in domain for blacklistedString in domainStringBlacklist):
                    print("ComboSquatting: ", end='')
                    print(domain.replace(f"{secondLevelDomain}-", color(f"{secondLevelDomain}-", 'RED')))
            if f"-{secondLevelDomain}" in domain:
                if not any(blacklistedString in domain for blacklistedString in domainStringBlacklist):
                    print("ComboSquatting: ", end='')
                    print(domain.replace(f"-{secondLevelDomain}", color(f"-{secondLevelDomain}", 'RED')))
        case 3:
            if f"{secondLevelDomain}-" in domain:
                if not any(blacklistedString in domain for blacklistedString in domainStringBlacklist):
                    print("ComboSquatting: ", end='')
                    print(domain.replace(f"{secondLevelDomain}-", color(f"{secondLevelDomain}-", 'RED')))
        case 4:
            if f"-{secondLevelDomain}" in domain:
                if not any(blacklistedString in domain for blacklistedString in domainStringBlacklist):
                    print("ComboSquatting: ", end='')
                    print(domain.replace(f"-{secondLevelDomain}", color(f"-{secondLevelDomain}", 'RED')))
        case 5:
            if f"-{monitoredDomain}" in domain:
                if not any(blacklistedString in domain for blacklistedString in domainStringBlacklist):
                    print("ComboSquatting: ", end='')
                    print(domain.replace(f"-{monitoredDomain}", color(f"-{monitoredDomain}", 'RED')))

def detectTLDSquatting(monitoredDomain, domain, domainStringBlacklist):

    # This will detect TLD Squatting attempts or show live domains that are already TLD squatting your monitored domain. 
    # That means if a domain exists(and subdomain is added and shows up in CT log) or is freshly registered you will be alerted if it looks like a TLD squatting attempt
    # Example: example.com ----> example.team is registered and HR-impersonating emails are sent.

    monitoredSecondLevelDomain = monitoredDomain.split(".")[-2]  # Get last element of the domainArray which by definition will always be the TLD(Top Level Domain) (assuming domains are provided as main.com and not main.com. or .com.main)
    secondLevelDomain = domain.split(".")[-2]  # Get last element of the domainArray which by definition will always be the TLD(Top Level Domain) (assuming domains are provided as main.com and not main.com. or .com.main)

    monitoredTopLevelDomain = monitoredDomain.split(".")[-1]     # Get last element of the domainArray which by definition will always be the TLD(Top Level Domain) (assuming domains are provided as main.com and not main.com. or .com.main)
    topLevelDomain = domain.split(".")[-1]  # Get last element of the domainArray which by definition will always be the TLD(Top Level Domain) (assuming domains are provided as main.com and not main.com. or .com.main)

    global secondAndTopLevelDomainVisitedList


    if(secondLevelDomain == monitoredSecondLevelDomain):
        if(topLevelDomain != monitoredTopLevelDomain):
            secondAndTopLevelDomain = secondLevelDomain + "." + topLevelDomain
            if secondAndTopLevelDomain not in secondAndTopLevelDomainVisitedList: 
                if not any(blacklistedString in domain for blacklistedString in domainStringBlacklist):
                    print("TLDSquatting: ", end='')
                    print(domain.replace(secondAndTopLevelDomain, color(secondAndTopLevelDomain, 'RED')))
                    secondAndTopLevelDomainVisitedList.append(secondAndTopLevelDomain)

def detectTypoSquatting(monitoredDomain, domain, domainStringBlacklist):

    monitoredSecondLevelDomain = monitoredDomain.split(".")[-2]  # Get last element of the domainArray which by definition will always be the TLD(Top Level Domain) (assuming domains are provided as main.com and not main.com. or .com.main)
    secondLevelDomain = domain.split(".")[-2]  # Get last element of the domainArray which by definition will always be the TLD(Top Level Domain) (assuming domains are provided as main.com and not main.com. or .com.main)

    damerauLevenshteinSimilaritySLD = DamerauLevenshtein.normalized_similarity(secondLevelDomain, monitoredSecondLevelDomain) # Only compare Second Level Domain. Useful extra detection Because CT Log also often is just a new subdomain and always doing

                                                                                                               # a full string comparision might lead to missed true positives for potential phishing domains
    if(damerauLevenshteinSimilaritySLD >= commandLineLogic.getDamerauLevensheinSimilarityTreshhold()):
        if(secondLevelDomain != monitoredSecondLevelDomain): # We don't want exact matches because it increases false positives and spam and our TLD Squatting detection method will handle it
            if not any(blacklistedString in domain for blacklistedString in domainStringBlacklist):
                print("TypoSquatting: ", end='')
                print(f"{domain.replace(secondLevelDomain, color(secondLevelDomain, 'RED'))} is {int(round(damerauLevenshteinSimilaritySLD, 2) * 100 )}% similar to {monitoredDomain}")


def detectLevelSquatting(monitoredDomain, domain, domainStringBlacklist):

    # This will detect LevelSquatting. In LevelSquatting an attacker registers a domain like amazon.google.attacker.org trying to phish
    # victims by impersonating amazon or google, when in reality it is just a subdomain of an arbitiary domain the Attacker controlls

    domainList = domain.split(".")

    monitoredSecondLevelDomain = monitoredDomain.split(".")[-2]
    secondLevelDomain = domain.split(".")[-2]

    if monitoredSecondLevelDomain in domainList and monitoredSecondLevelDomain != secondLevelDomain:
        if not any(blacklistedString in domain for blacklistedString in domainStringBlacklist):
            print("LevelSquatting: ", end='')
            print(domain.replace(monitoredSecondLevelDomain, color(monitoredSecondLevelDomain, 'RED')))


def streamIngest(domain):

    global comboSquattingDetectionTreshold
    comboSquattingDetectionTreshold = commandLineLogic.getComboSquattingDetectionMethod()
    monitoredDomainsList = commandLineLogic.getMonitoredDomainsList()

    domainStringBlacklist = commandLineLogic.getDomainStringBlacklist()

    excludedDetectionModeList = commandLineLogic.getExcludedDetectionModeList()

    for monitoredDomain in monitoredDomainsList:
        monitoredDomain = monitoredDomain.split("\n")[0] # The string includes a \n at the end which we need to remove for proper parsing later

        if "combo" not in excludedDetectionModeList:
            detectComboSquatting(monitoredDomain, domain, domainStringBlacklist)
        if "tld" not in excludedDetectionModeList:
            detectTLDSquatting(monitoredDomain, domain, domainStringBlacklist)
        if "typo" not in excludedDetectionModeList:
            detectTypoSquatting(monitoredDomain, domain, domainStringBlacklist)     # Pretty sure adding AI detection to Damerau Levenshtein treshhold of >= 0.8(my default) doesn't make any sense because hallucinations
                                                                                    # and unclear cases will only increase the rate of false positives. I even tried it with gemini and it wasn't that good...
                                                                                    # On top of that the false positive rate with a treshold of >= 0.8 is pretty low and there are bigger battles to fight rn
        if "level" not in excludedDetectionModeList:
            detectLevelSquatting(monitoredDomain, domain, domainStringBlacklist)
