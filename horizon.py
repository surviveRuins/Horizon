import websocket
import json

def onMessage(ws, message):
    # A new domain was added to a Certificate Transparency Log, my certwatch server detected the change in a 
    # Certificate Transparency log and streamed the new domains to my client. This onMessage function handles each domain
    newDomains = json.loads(message)
    newDomainsList = newDomains["data"] # It is not just 1 domain always, there could be many in the `data` field and we want to save and iterate via list
    for newDomain in newDomainsList:
        print(newDomain)

def onError(ws, error):
    print(f"Encountered error: {error}")

def onClose(ws, closeStatusCode, closeMsg):
    print("Connection closed")

def onOpen(ws):
    print("Connection opened")
    ws.send("Hello, Server!")

if __name__ == "__main__": 
    # wss:// connects only on https and ws:// connects only on http. Since my server doesn't have a TLS cert and is direct IP address we will use ws://
    ws = websocket.WebSocketApp("ws://138.199.224.29:8080/domains-only",   
                                on_message=onMessage,
                                on_error=onError,
                                on_close=onClose)
    ws.on_open = onOpen
    ws.run_forever()
