import json
import pandas as pd
import base64

import seaborn as sns
from matplotlib import pyplot as plt

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
    
    
    def training_progress(self, training_id = None):
        
        if training_id == None:
            training_id = self.latest_training_id

        return json.dumps(
            {'action': 'training_progress', 
             'training_id': training_id, 
             'payload': {'epoch_iter': 0, 
                         'epoch_total': 10, 
                         'batch_iter': 0, 
                         'batch_total': 10, 
                         'task': 'train'}})

    
    def metric_image(self, training_id = None, epoch = None):
        
        if training_id == None:
            training_id = self.latest_training_id
            
            if epoch == None:
                training = self.trainings.get(training_id)
                training.stats.epoch.max().values()
        
        try:
            with open(f'./app/img/metrics_{training_id}.png', "rb") as img:
                img64 = base64.b64encode(img.read()).decode('utf-8')
        except:
            with open(f'./app/img/plain.png', "rb") as img:
                img64 = base64.b64encode(img.read()).decode('utf-8')
                
        return json.dumps({'action': 'metric_image', 'training_id': training_id, 'epoch' : epoch, 'image': img64}, indent = 2)
        
        
class _Training():
    
    def __init__(self, training_id):
        self.training_id = training_id
        self.stats = None
        self.config = None
        self.metrics = None
        self.metrics_label = None
        
    def add_stats(self, data):
        
        if not isinstance(self.stats, pd.DataFrame):
            self.metrics = [metric for (metric, val) in data.items() if metric not in (['training_id', 'epoch', 'train_loss', 'valid_loss', 'time'])]
            self.stats = pd.DataFrame(data, index=[0])#, orient='index', columns = data.keys())
        else:
            self.stats = self.stats.append(pd.DataFrame(data, index=[0])).reset_index(drop = True)
        
        self.metrics_label = [f'{metric.split("_")[0]} ({val: .5f})' for (metric, val) in data.items() if metric not in (['training_id', 'epoch', 'train_loss', 'valid_loss', 'time'])]
            
        # generate metrics image
        self._gen_metrics_image()
        
        
    def add_config(self, data):
        self.config = _TrainingConfig.fromJson(data)

    
    def _gen_metrics_image(self):
            stats = self.stats[['epoch'] + self.metrics]
            stats.columns = ['epoch'] + self.metrics_label            
                        
            stats = pd.melt(stats[['epoch'] + self.metrics_label], id_vars=['epoch'], value_vars = self.metrics_label)
            stats.columns = ['epoch','Metrics','value']

            sns.set(rc={'axes.facecolor':'black', 
                        'figure.facecolor':'black',
                        'patch.linewidth': 0.0,
                        'text.color': '1',
                        'axes.edgecolor': 'black',
                        'figure.figsize':(3, 3)
                       })

            fig, ax = plt.subplots()

            g=sns.lineplot(x='epoch', y='value',
                         hue='Metrics',
                         data=stats,
                         linewidth = 4,
                         #legend = False, 
                         marker="o", 
                         ax=ax
                         )

            g.set(xticks=[])
            g.set(yticks=[]) 
            g.set(xlabel='') 
            g.set(ylabel='')
            
            # https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.legend.html
            fig.tight_layout(pad=1.08, rect=(0, 0.02 + 0.06 * len(self.metrics_label), 1, 0.9))
            
            fig.get_axes()[0].legend(loc='lower center', 
                                     #loc='best', 
                                     bbox_to_anchor=(0.5, -0.15 * len(self.metrics_label)),
                                     fontsize = 10, 
                                     handlelength = 0,
                                     handletextpad = -2,
                                     #facecolor='white',
                                     #framealpha = 0.2, 
                                     labelcolor = 'linecolor'
                                    ) 
            
            # fix size to 336x336
            fig.set_size_inches(3, 3)
            fig.savefig(f'app/img/metrics_{self.training_id}.png', dpi = 112)
            
        

class _TrainingConfig():
    
    def __init__(self, config = None):
        self.config = config

    @classmethod
    def fromJson(cls, data):
        data =json.loads(data)
        
        return cls(config = data)

        