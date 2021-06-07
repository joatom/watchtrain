from abc import abstractmethod
from fastapi import WebSocket

from app.topics.pc import PC

class Consumer(PC):
        
    @abstractmethod
    def handle_request(self, data):
        pass         
    

    
