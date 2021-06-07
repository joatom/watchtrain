from fastai.basics import *
import json
import pandas as pd
import websocket 
import time
        
# code heavily influenced by CSVLogger and ProgressCallback (https://github.com/fastai/fastai/blob/master/fastai/callback/progress.py)

class WebsocketLogger(Callback):
    # callback execution order (after recorder (50))
    order = 80
    def __init__(self, conn, params = None):
        self.conn = conn
        self.params = params
        #websocket.enableTrace(True)
        
        self.training_id = self._req_training_id()
    
    
    def before_train(self): 
        self.batch_iter = 0
        self.task = 'train'        
        self._send_train_progress()
    
    def before_validate(self): 
        self.batch_iter = 0
        self.task = 'valid'
        self._send_train_progress()
    
    def after_batch(self):
        self.batch_iter += 1
        if (self.batch_iter%(len(self.dl)//9) == 0) | (self.batch_iter == len(self.dl)):
            self._send_train_progress()

    def before_fit(self):
        "Prepare file with metric names."
        if hasattr(self, "gather_preds"): return
        
        self.data = {}
        self.columns = ['training_id'] + list(self.recorder.metric_names)
        
        # register logger
        self.old_logger,self.learn.logger = self.logger,self._write_line

    def _write_line(self, log):
        "Write a line with `log` and call the old logger."
        
        # log[0] is the epoch number
        self.data[log[0]] = dict(zip(self.columns, [self.training_id] + list(log)))
        
        self._conn_send(json.dumps({'action': 'training stats', 'training_id': self.training_id, 'payload': self.data[log[0]]}, indent = 2))
        
        self.old_logger(log)

    def after_fit(self):
        "Close the file and clean up."
        if hasattr(self, "gather_preds"): return
        self.learn.logger = self.old_logger

    
    def _send_train_progress(self):
        self._conn_send(json.dumps({'action': 'training progress', 
                                    'training_id': self.training_id, 
                                    'payload': {'epoch_iter': self.epoch+1, 
                                                'epoch_total': self.n_epoch,
                                                'batch_iter': self.batch_iter, 
                                                'batch_total': len(self.dl),
                                                'task': self.task}}, indent = 2))

    
    def _req_training_id(self):
        msg = json.dumps({'action': 'Requesting training_id', 'training_id': '', 'payload': ''}, indent = 2)
        
        ws = websocket.create_connection(self.conn)
        ws.send(msg)
        
        # wait for response, other wise msg gets lost
        training_id = ws.recv()
        
        ws.close()
        
        return training_id
    
    def _conn_send(self, msg):
        ws = websocket.create_connection(self.conn)
        ws.send(msg)
        
        # wait for response, other wise msg gets lost
        #if ws.recv():
        #    pass
        
        ws.close()
        

    