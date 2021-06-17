from abc import ABC, abstractmethod
from fastapi import WebSocket


class Agent(ABC):
    
    def __init__(self, websocket, client_id = None, verbose = 0):
        self.websocket = websocket
        self.client_id = client_id
        self.verbose = verbose
            
    @abstractmethod
    def handle_request(self, data):
        pass