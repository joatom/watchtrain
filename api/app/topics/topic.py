from fastapi import WebSocket

from app.topics.agent import Agent
from app.topics.producer_agent import ProducerAgent
from app.topics.consumer_agent import ConsumerAgent
            
class Topic():

    """
    Defines a topic and setup connection managers for producers and consumers.
    """
    
    def __init__(self):
        self.producer_manager = _ConnectionManager()
        self.consumer_manager = _ConnectionManager()
    
    async def connect(self, agent):
        
        if isinstance(agent, ProducerAgent):
            await self.producer_manager.connect(agent)
        else:
            await self.consumer_manager.connect(agent)

    def disconnect(self, agent):
        
        if isinstance(agent, ProducerAgent):
            self.producer_manager.disconnect(agent)
        else:
            self.consumer_manager.disconnect(agent)

   
            
class _ConnectionManager:
    
    """
    Connection Manager from the fastapi tutorial:
    https://fastapi.tiangolo.com/advanced/websockets/#handling-disconnections-and-multiple-clients)
    """
    
    def __init__(self):
        self.active_connections: List[Agent] = []

    async def connect(self, agent: Agent):
        await agent.websocket.accept()        
        self.active_connections.append(agent)
        
    def disconnect(self, agent: Agent):
        self.active_connections.remove(agent)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, verbose: int = 0):
        for connection in self.active_connections:
            if connection.verbose >= verbose:
                await connection.websocket.send_text(message)

            
            