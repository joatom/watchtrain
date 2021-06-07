from fastapi import WebSocket
from app.topics.consumer import Consumer
from app.topics.watch_training.topic import WatchTrainingTopic

class VerboseConsumer(Consumer):
    
    async def handle_request(self, data, topic: WatchTrainingTopic):
        
        print('consumer', data)
        
        await self.websocket.send_text(data)

class WatchConsumer(Consumer):
    
    async def handle_request(self, data, topic: WatchTrainingTopic):
        print('WatConcn')
        