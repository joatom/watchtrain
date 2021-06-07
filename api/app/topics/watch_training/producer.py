from app.topics.producer import Producer
from fastapi import WebSocket
from app.topics.watch_training.topic import WatchTrainingTopic
import json

class TrainDataProducer(Producer):
    
    async def handle_request(self, data, topic: WatchTrainingTopic):
        
        data = json.loads(data)
        
        print('producer', data)
        
        if data['action'] == 'Requesting training_id':
            
            topic.new_training()
            await self.websocket.send_text(f"{topic.latest_training_id}")
            await topic.consumer_manager.broadcast(f'New Training with ID {topic.latest_training_id} just started ...', verbose = 1)
            
        if data['action'] == 'training stats':
            
            try:
                topic.trainings[int(data['training_id'])].add_stats(data['payload'])
            except KeyError as e:
                # if API-Server got restarted and training is still running. A given training_id can be used to continue tracking.
                topic.new_training(force_training_id = int(data['training_id']))
                topic.trainings[int(data['training_id'])].add_stats(data['payload'])                
                
            #await self.websocket.send_text(f"recieved the data")
            await topic.consumer_manager.broadcast(data['training_id'], verbose = 1)
            await topic.consumer_manager.broadcast(json.dumps(data['payload']), verbose = 1) #topic.trainings[int(data['training_id'])].stats.to_string())

    
        if data['action'] == 'training progress':
            await topic.consumer_manager.broadcast(json.dumps(data), verbose = 0)
            