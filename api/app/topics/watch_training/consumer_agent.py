from fastapi import WebSocket
from app.topics.consumer_agent import ConsumerAgent
from app.topics.watch_training.topic import WatchTrainingTopic

class VerboseConsumerAgent(ConsumerAgent):
    
    async def handle_request(self, data, topic: WatchTrainingTopic):
        
        print(f'consumer #{self.client_id}: {data}')
        
        await self.websocket.send_text(data)

class WatchConsumerAgent(ConsumerAgent):
    
    async def handle_request(self, data, topic: WatchTrainingTopic):
        print('WatConcn')
        