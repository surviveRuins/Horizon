import websocket
import websocketHandler
import commandLineLogic

def connect():
    # wss:// connects only on https and ws:// connects only on http. Since my server doesn't have a TLS cert and is direct IP address we will use ws://
    ws = websocket.WebSocketApp(commandLineLogic.getCertstreamURL(),   
                                on_message=websocketHandler.onMessage,
                                on_error=websocketHandler.onError,
                                on_close=websocketHandler.onClose)
    ws.on_open = websocketHandler.onOpen
    ws.run_forever()
