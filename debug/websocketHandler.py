import json
import sys
import domainStreamHandler

def onMessage(ws, message):
    # A new domain was added to a Certificate Transparency Log, my certwatch server detected the change in a 
    # Certificate Transparency log and streamed the new domains to my client. This onMessage function handles each domain
    newDomains = json.loads(message)
    newDomainsList = newDomains["data"] # It is not always just 1 domain, there could be many in the `data` field and we want to save and iterate via list 

    for newDomain in newDomainsList:
        if "*." in newDomain:                       # Detect Wildcards 
            newDomain = newDomain[2:]               # Normalize them to regular domains by removing the *. in *.example.com 
        
        domainStreamHandler.streamIngest(newDomain) 

def onError(ws, error):
    print(f"Encountered error: {error}")

def onClose(ws, closeStatusCode, closeMsg):
    print("Connection closed")

def onOpen(ws):
    print("Connection opened")
    ws.send("Hello, Server!")
