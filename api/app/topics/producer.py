from abc import abstractmethod
from fastapi import WebSocket

from app.topics.pc import PC

class Producer(PC):
    
    @abstractmethod
    def handle_request(self, data):
        pass         
    
