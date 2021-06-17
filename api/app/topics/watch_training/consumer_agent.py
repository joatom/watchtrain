from fastapi import WebSocket
import json
from app.topics.consumer_agent import ConsumerAgent
from app.topics.watch_training.topic import WatchTrainingTopic


class VerboseConsumerAgent(ConsumerAgent):
    
    
    async def handle_request(self, data, topic: WatchTrainingTopic):
        
        data = json.loads(data)
        
        if data['action'] == 'connected':
            training_id = topic.latest_training_id
            
            await self.websocket.send_text(topic.metric_image(training_id = training_id))
            await self.websocket.send_text(topic.training_progress(training_id = training_id))
        
        else:
            await self.websocket.send_text(json.dumps(data))
        
    
    
class WatchConsumerAgent(ConsumerAgent):
    
    
    async def handle_request(self, data, topic: WatchTrainingTopic):
        
        data = json.loads(data)
        
        if data['action'] == 'connected':
            training_id = topic.latest_training_id
            
            await self.websocket.send_text(topic.metric_image(training_id = training_id))
            await self.websocket.send_text(topic.training_progress(training_id = training_id))
        
        