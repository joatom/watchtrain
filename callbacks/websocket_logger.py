from fastai.basics import *
import json
import pandas as pd
import websocket 
import time
try:
    import thread
except ImportError:
    import _thread as thread

import threading

# code heavily influenced by CSVLogger and ProgressCallback (https://github.com/fastai/fastai/blob/master/fastai/callback/progress.py)
# and websocket-client (https://github.com/websocket-client/websocket-client)

class WebsocketLogger(Callback):
    
    # callback execution order needs to be after recorder (50)
    order = 80
    
    def __init__(self, conn, params = None):
        self.conn = conn
        self.params = params
        
        #websocket.enableTrace(True)
        
        self._ws_connect()
        
        self.training_id = self._req_training_id()
    
    
    ############    
    # callback #
    ############
    
    
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
        self.ws.send(json.dumps({'action': 'debug', 'value':'BEFORE FIT'}))
        self.data = {}
        self.columns = ['training_id'] + list(self.recorder.metric_names)
        
        # register logger
        self.old_logger,self.learn.logger = self.logger,self._write_line

    def after_fit(self):
        "Close the file and clean up."
        if hasattr(self, "gather_preds"): return
        self.ws.send(json.dumps({'action': 'debug', 'value':'AFTER FIT'}))
        self.learn.logger = self.old_logger
        
        self.ws.close()
        
    def after_cancel_fit(self):
        print('canceled fit')
        self.ws.close()
        
        
    ###################    
    # logger helpers #
    ###################    
        
        
    def _write_line(self, log):
        "Write a line with `log` and call the old logger."
        
        # log[0] is the epoch number
        self.data[log[0]] = dict(zip(self.columns, [self.training_id] + list(log)))
        
        self.ws.send(json.dumps({'action': 'training stats', 'training_id': self.training_id, 'payload': self.data[log[0]]}, indent = 2))
        
        self.old_logger(log)

        
    #####################    
    # websocket helpers #
    #####################    
    
    
    def _send_train_progress(self):
        self.ws.send(json.dumps({'action': 'training_progress', 
                                    'training_id': self.training_id, 
                                    'payload': {'epoch_iter': self.epoch+1, 
                                                'epoch_total': self.n_epoch,
                                                'batch_iter': self.batch_iter, 
                                                'batch_total': len(self.dl),
                                                'task': self.task}}, indent = 2))

    
    def _req_training_id(self):
        
        msg = json.dumps({'action': 'Requesting training_id', 'training_id': '', 'payload': ''}, indent = 2)
        
        self.ws.send(msg)
        
        data = self.ws.sock.recv()
        
        training_id = json.loads(data)['training_id']
        
        print(f'Training id : {training_id}')
        
        return training_id
        
    
    def _on_ws_message(self,ws, message):
        print(message)

    def _on_ws_error(self,ws, error):
        print('Websocket error:',error)

    def _on_ws_close(self,ws, close_status_code, close_msg):
        print('Websocket connection closed.')

    def _on_ws_open(self,ws):
        # ws connection is now ready => unlock
        self.ws_ready_lock.release()
        
    def _ws_connect(self):
        
        # aquire lock until websocket is ready to use
        self.ws_ready_lock = threading.Lock()
        self.ws_ready_lock.acquire()
        
        print('Connecting websocket ...')
        
        self.ws = websocket.WebSocketApp(self.conn,
                                          on_open = self._on_ws_open,
                                          on_message = self._on_ws_message,
                                          on_error = self._on_ws_error,
                                          on_close = self._on_ws_close)

        # run websocket in background
        thread.start_new_thread(self.ws.run_forever, ())
        
        # wait for websocket to be initialized
        self.ws_ready_lock.acquire()
        
        print('... websocket connected.')
        
         