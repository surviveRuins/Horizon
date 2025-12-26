import websocket
import websocketHandler

def connect():
    # wss:// connects only on https and ws:// connects only on http. Since my server doesn't have a TLS cert and is direct IP address we will use ws://
    ws = websocket.WebSocketApp("ws://138.199.224.29:8080/domains-only",   
                                on_message=websocketHandler.onMessage,
                                on_error=websocketHandler.onError,
                                on_close=websocketHandler.onClose)
    ws.on_open = websocketHandler.onOpen
    ws.run_forever()
