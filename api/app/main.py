from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
import pandas as pd
import json
import time

import app.topics.topic as tp
import app.topics.watch_training.topic as wt_topic
from app.topics.watch_training.producer_agent import TrainDataProducerAgent
from app.topics.watch_training.consumer_agent import VerboseConsumerAgent

app = FastAPI()

@app.get("/hello")
async def root():
    return {"message": "Hello xJT World"}


@app.get("/img")
async def main():
    return FileResponse("/app/img/336_my.jpg", media_type="image/jpeg")


@app.get("/epochs/last")
async def last_epoch():
    return {"epoch": 10}

@app.get("/epochs/{epoch_id: int}")
async def epoch_by_id(epoch_id):
    return {"epoch": epoch_id}

#@app.get("/epochs/")
#async def epoch_range(from: int = 0, to: Optional[int] = None):
#    if to:
#        r = range(from, to)
#    else: 
#        r = range(10)
#    
#    return {"epochs": [{"epoch_id": e} for e in e]}


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>Verbose Consumer</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            Debug message: <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <span id='progress'>
        </span>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://maichine:8555/ws/watchtrain/consumer/${client_id}`);
            ws.onmessage = function(event) {
                var data = JSON.parse(event.data);
                if (data.action == 'training progress') {
                    document.querySelector("#progress").textContent = 'Epoch: ' + data.payload['epoch_iter'] + '/' + data.payload['epoch_total'] +
                                                                      ' | Batch (' + data.payload['task'] + '): ' + data.payload['batch_iter'] + '/' + data.payload['batch_total']
                }
                else{
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                }
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send('{"action":"debug", "value":"'+input.value+'"}')
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)


topic = {}


@app.get("/{topic_name}/summary")
async def get(topic_name: str):
    global topic
    
    if topic.get(topic_name) == None:
        summary = json.dumps({'summary' : 'No training yet.'}, indent = 2)
    else:
        summary = topic[topic_name].summary()
        
    if summary == None:
        summary = json.dumps({'summary' : 'Training just started.'}, indent = 2)
    
    return summary


@app.websocket("/ws/{topic_name}/{agent}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, topic_name: str, agent: str, client_id: int):
    global topic
    
    assert agent in ['producer', 'consumer']
    
    if topic_name == 'watchtrain':
        
        # init topic if not exists
        if topic.get(topic_name) == None:
            topic[topic_name] = wt_topic.WatchTrainingTopic()
        
        # register producer or consumer
        if agent == 'producer':
            agent = TrainDataProducerAgent(websocket, client_id)
        else:
            agent = VerboseConsumerAgent(websocket, client_id, verbose = 1)            
        
        # connect
        await topic[topic_name].connect(agent)

        # handle incoming data
        try:
            while True:
                data = await websocket.receive_text()

                await agent.handle_request(data, topic[topic_name])

        except WebSocketDisconnect:
            # disconnect
            topic[topic_name].disconnect(agent)

    else:
        raise ValueError(f'Topic *{topic_name}* not implemented')

        
