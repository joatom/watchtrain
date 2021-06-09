from abc import abstractmethod
from fastapi import WebSocket

from app.topics.agent import Agent

class ProducerAgent(Agent):
    
    @abstractmethod
    def handle_request(self, data):
        pass         
    
