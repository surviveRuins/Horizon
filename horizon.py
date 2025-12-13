import websocket

def onMessage(ws, message):
    print(f"Received message: {message}")

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
