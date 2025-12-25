import sys
from rapidfuzz.distance import DamerauLevenshtein

# This is the handler for the domain stream coming in, We get raw domains with wildcards removed as a string.
# Everytime the streamIngest function is called 1 new domain was sent to the websocket client by my server.
# I can't really believe it either but all the processing doesn't seem to slow the websocket down enough to fall behind the newest state.
# I did some testing by printing them all here and running wscat on a seperate maschine but it genuinly seems to work perfectly.

monitoredDomainsList = []
counter = 0
comboSwappingDetectionTreshold = 4; # 1: flag any domain that has the string of the secondLevelDomain in it
                                    # 2: flag any domain that "secondLevelDomain-" (or _) in it. example-login.com will be flagged examplelogin.com will not be flagged for monitored domain example.com
                                    # 3: flag any domain that has "-secondLevelDomain" (or _) in it. login-example-uber.com will be flagged, example-login.com will not be flagged
                                    # 4: flag any domain that has "-secondLevelDomain.topLevelDomain" (or _) in it(meaning it has to end on our Fully qualified monitored domain.
                                    #    login-example.com will be flagged, login-example-uber.com will not be flagged

with open(sys.argv[1], "r") as file:
    for monitoredDomain in file:
        monitoredDomainsList.append(monitoredDomain)

def detectComboSwapping(monitoredDomain, domain):
    # Assumption for our list of monitored domains from the file given by the user in sys.argv[1]: One domain in format main.tld per line: 
    # That means we need to seperate the `main` part as that is the only relevant thing for comboswapping: paypal.com --> paypal --> now we can detect if the streamIngest() data contains paypal as a signal for comboswapping
    # In paypal.com the `.com` is called TLD(Top Level Domain) and the `paypal` is called SLD(Second Level Domain)
    
    secondLevelDomain = monitoredDomain.split(".")[0]

    match(comboSwappingDetectionTreshold):
        case 1:
            if secondLevelDomain in domain:
                print(domain)
        case 2:
            if f"{secondLevelDomain}-" in domain or f"{secondLevelDomain}_" in domain:
                print(domain)
        case 3:
            if f"-{secondLevelDomain}" in domain or f"_{secondLevelDomain}" in domain:
                print(domain)
        case 4:
            if f"-{monitoredDomain}" in domain or f"_{monitoredDomain}" in domain:
                print(domain)

def detectTLDSquatting(monitoredDomain, domain):
    print(monitoredDomain)
            



def streamIngest(domain):
    for monitoredDomain in monitoredDomainsList:
        detectComboSwapping(monitoredDomain, domain)
        #damerauLevenshteinSimilarity = DamerauLevenshtein.normalized_similarity(domain, monitoredDomain)   # This is calculated by using the distance, normalizing it to a range of [0,1] and then
                                                                                                           # doing `1 - normalized_distance`. So for a damerauLevenshteinDistance of 4: 4 --> 0.4 --> 1 - 0.4 = 0.6 Similarity
        #if(damerauLevenshteinSimilarity > 0.5):
        #print(domain)
