import json
import pandas as pd

from app.topics.topic import Topic
from app.utils import Sequence

class WatchTrainingTopic(Topic):
    
    def __init__(self):
        super(WatchTrainingTopic,self).__init__()
        self.trainings = {}
        self.seq_training_id = Sequence(0)
        self.latest_training_id = self.seq_training_id.curval()
        
    def new_training(self, force_training_id = None):
        
        # if API-Server got restarted and training is still running. A given training_id can be used to continue tracking.
        if force_training_id:
            self.seq_training_id = Sequence(force_training_id)
            self.latest_training_id = self.seq_training_id.curval()
        else:
            self.latest_training_id = self.seq_training_id.nextval()
        
        self.trainings[self.latest_training_id] = _Training(self.latest_training_id)
        
    def summary(self, training_id = None):
        
        if training_id == None:
            training_id = self.latest_training_id
        
        training = self.trainings.get(training_id)
        
        if training_id == 0:
            summary = 'No training yet.'
        elif training == None:
            summary = f'Training # {training_id} not found.'
        else:
            stats = training.stats
            
            if not isinstance(stats,pd.DataFrame):
                summary = f'No statistics for training # {training_id} available, yet.'
            else:
                summary = stats.to_dict('index') # to_json(orient="index", double_precision=6) #orient="records"
        
        return json.dumps({'summary': summary}, indent = 2)
        
        
class _Training():
    
    def __init__(self, training_id):
        self.training_id = training_id
        self.stats = None
        self.config = None
        self.metrics = None
        
    def add_stats(self, data):
        
        if not isinstance(self.stats, pd.DataFrame):
            self.metrics = [metric for (metric, val) in data.items() if metric not in (['training_id', 'epoch', 'train_loss', 'valid_loss', 'time'])]
            self.stats = pd.DataFrame(data, index=[0])#, orient='index', columns = data.keys())
        else:
            self.stats = self.stats.append(pd.DataFrame(data, index=[0])).reset_index(drop = True)
                
    def add_config(self, data):
        self.config = _TrainingConfig.fromJson(data)

        
"""class _TrainingStats():
    
    def __init__(self, epoch = None, train_loss = None, valid_loss = None, metrics = None, time = None):
        self.epoch = epoch
        self.train_loss = train_loss
        self.valid_loss = valid_loss
        self.metrics = metrics
        self.time = time

    @classmethod
    def fromDict(cls, data):
        #data = json.loads(data)
        
        #metrics = {metric:val for (metric, val) in data.items() if metric not in (['training_id', 'epoch', 'train_loss', 'valid_loss', 'time'])}
        training_id = data.pop('training_id')
        epoch = data.pop('epoch')
        train_loss = data.pop('train_loss')
        valid_loss = data.pop('valid_loss')
        time = data.pop('time')
        
        #remaining data is metrics
        metrics = data
        
        return cls(epoch = epoch, train_loss = train_loss, valid_loss = valid_loss, metrics = metrics, time = time)
"""

class _TrainingConfig():
    
    def __init__(self, config = None):
        self.config = config

    @classmethod
    def fromJson(cls, data):
        data =json.loads(data)
        
        return cls(config = data)

        