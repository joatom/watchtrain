from app.topics.producer_agent import ProducerAgent
from fastapi import WebSocket
from app.topics.watch_training.topic import WatchTrainingTopic
import json


class TrainDataProducerAgent(ProducerAgent):
    
    
    async def handle_request(self, data, topic: WatchTrainingTopic):
        
        data = json.loads(data)
        
        print(f'producer #{self.client_id}: {data}')
        
        
        if data['action'] == 'Requesting training_id':
            
            topic.new_training()
            await self.websocket.send_text(json.dumps({'training_id': topic.latest_training_id}))
            
            # Verbose
            await topic.consumer_manager.broadcast(f'New Training with ID {topic.latest_training_id} just started ...', verbose = 1)
            
            
        if data['action'] == 'training stats':
        
            stats = data['payload']
            
            try:
                topic.trainings[int(data['training_id'])].add_stats(stats)
            except KeyError as e:
                # if API-Server got restarted and training is still running. A given training_id can be used to continue tracking.
                topic.new_training(force_training_id = int(data['training_id']))
                topic.trainings[int(data['training_id'])].add_stats(stats)                
            
            await topic.consumer_manager.broadcast(json.dumps({'action': 'new_stats','training_id': data['training_id']}))
            await topic.consumer_manager.broadcast(topic.metric_image(training_id = data['training_id'], epoch = stats.get('epoch')))
            
            # Verbose
            await topic.consumer_manager.broadcast(json.dumps({'training_id': data['training_id']}), verbose = 1)
            await topic.consumer_manager.broadcast(json.dumps(data['payload']), verbose = 1)

    
        if data['action'] == 'training_progress':
            await topic.consumer_manager.broadcast(json.dumps(data), verbose = 0)
        
        
        if data['action'] == 'debug':
            await topic.consumer_manager.broadcast(json.dumps(data), verbose = 1)
         