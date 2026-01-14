import json
import sys
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
import domainStreamHandler
import commandLineLogic


processedDomainsCounter = 0
console = Console()
live = Live(console = console, refresh_per_second = 1)  # This cannot be initialized in a function that is called more than once in horizon or it will spam the terminal
                                                            # To update the one `Live` object we have we strictly use live.update and that can be called in while loops and works as expected 

def onMessage(ws, message):
    # A new domain was added to a Certificate Transparency Log, my certwatch server detected the change in a 
    # Certificate Transparency log and streamed the new domains to my client. This onMessage function handles each domain
    newDomains = json.loads(message)
    newDomainsList = newDomains["data"] # It is not always just 1 domain, there could be many in the `data` field and we want to save and iterate via list 

    for newDomain in newDomainsList:
        if "*." in newDomain:                       # Detect Wildcards 
            newDomain = newDomain[2:]               # Normalize them to regular domains by removing the *. in *.example.com 
        
        domainStreamHandler.streamIngest(newDomain)

        if not commandLineLogic.getDisableProgressBar():
            global processedDomainsCounter
            processedDomainsCounter += 1
            live.update(Panel(f"Domains processed: {processedDomainsCounter}"))

def onError(ws, error):
    pass

def onClose(ws, closeStatusCode, closeMsg):
    if not commandLineLogic.getDisableProgressBar():
        live.stop()
    print("Connection closed")

def onOpen(ws):
    print(f"\nSuccessfully connected to certstream websocket at {commandLineLogic.getCertstreamURL()}\n")
    if not commandLineLogic.getDisableProgressBar():
        live.start()
    ws.send("Hello, Server!")
