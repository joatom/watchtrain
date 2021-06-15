from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse

import pandas as pd
import json

import app.topics.topic as tp
import app.topics.watch_training.topic as wt_topic
from app.topics.watch_training.producer_agent import TrainDataProducerAgent
from app.topics.watch_training.consumer_agent import VerboseConsumerAgent, WatchConsumerAgent

app = FastAPI()


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
        <p>
            <img id="metric_image" width="360" />
        </p>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://maichine:8555/ws/watchtrain/verbose/${client_id}`);
            var metric_image = document.getElementById('metric_image');
            ws.onmessage = function(event) {
                var data = JSON.parse(event.data);
                if (data.action == 'training_progress') {
                    document.querySelector("#progress").textContent = 'Epoch: ' + data.payload['epoch_iter'] + '/' + data.payload['epoch_total'] +
                                                                      ' | Batch (' + data.payload['task'] + '): ' + data.payload['batch_iter'] + '/' + data.payload['batch_total']
                } else if (data.action == 'metric_image'){
                
                    metric_image.src = "data:image/png;charset=utf-8;base64, " + data.image;

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
    
    assert agent in ['producer', 'verbose', 'watch']
    
    if topic_name == 'watchtrain':
        
        # init topic if not exists
        if topic.get(topic_name) == None:
            topic[topic_name] = wt_topic.WatchTrainingTopic()
        
        # register producer or consumer
        if agent == 'producer':
            agent = TrainDataProducerAgent(websocket, client_id)
        elif agent == 'watch':
            agent = WatchConsumerAgent(websocket, client_id)
        else:
            agent = VerboseConsumerAgent(websocket, client_id, verbose = 1)            
        
        # connect
        await topic[topic_name].connect(agent)
        await agent.handle_request(json.dumps({'action': 'connected'}), topic[topic_name])
        
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

        

@app.get("/img")
async def main():
    print("Im request")
    return FileResponse("/app/img/metrics_1.png", media_type="image/png") 


@app.get("/{training_id}/img/{img_cat}")
async def img(training_id, img_cat):
    return FileResponse(f"/app/img/{img_cat}_{training_id}.png", media_type="image/png")

