from app.topics.producer_agent import ProducerAgent
from fastapi import WebSocket
from app.topics.watch_training.topic import WatchTrainingTopic
import json


class TrainDataProducerAgent(ProducerAgent):
    
    
    async def handle_request(self, data, topic: WatchTrainingTopic):
        
        data_dict = json.loads(data)
        
        print(f'producer #{self.client_id}: {data_dict}')
        
        
        if data_dict['action'] == 'register_training':
            
            topic.new_training()
            await self.websocket.send_text(json.dumps({'training_id': topic.latest_training_id, 'force_training_id': data_dict['training_id']}))
            
            # Broadcast metric image if broken connection is resumed or new training has been initialized
            await topic.consumer_manager.broadcast(topic.metric_image(training_id = data_dict['training_id']))
            
            # Verbose
            await topic.consumer_manager.broadcast(f'New Training with ID {topic.latest_training_id} just started ...', verbose = 1)
            
            
        if data_dict['action'] == 'training_stats':
        
            stats = data_dict['payload']
            
            try:
                topic.trainings[int(data_dict['training_id'])].add_stats(stats)
            except KeyError as e:
                # if API-Server got restarted and training is still running. A given training_id can be used to continue tracking.
                topic.new_training(force_training_id = int(data_dict['training_id']))
                topic.trainings[int(data_dict['training_id'])].add_stats(stats)                
            
            await topic.consumer_manager.broadcast(data)
            await topic.consumer_manager.broadcast(topic.metric_image(training_id = data_dict['training_id'], epoch = stats.get('epoch')))
            
            # Verbose
            await topic.consumer_manager.broadcast(json.dumps({'training_id': data_dict['training_id']}), verbose = 1)
            await topic.consumer_manager.broadcast(json.dumps(data_dict['payload']), verbose = 1)

    
        if data_dict['action'] == 'training_progress':
            await topic.consumer_manager.broadcast(data, verbose = 0)
        
        
        if data_dict['action'] == 'debug':
            await topic.consumer_manager.broadcast(data, verbose = 1)
         