from abc import ABC, abstractmethod
from fastapi import WebSocket


class PC(ABC):
    
    def __init__(self, websocket, verbose = 0):
        self.websocket = websocket
        self.verbose = verbose
            
    @abstractmethod
    def handle_request(self, data):
        pass         
    