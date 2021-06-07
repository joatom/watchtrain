from fastapi import WebSocket

from app.topics.pc import PC
from app.topics.producer import Producer
from app.topics.consumer import Consumer
            
class Topic():

    """
    Defines a topic and setup connection managers for producers and consumers.
    """
    
    def __init__(self):
        self.producer_manager = _ConnectionManager()
        self.consumer_manager = _ConnectionManager()
    
    async def connect(self, pc):
        
        if isinstance(pc, Producer):
            await self.producer_manager.connect(pc)
        else:
            await self.consumer_manager.connect(pc)

    def disconnect(self, pc):
        
        if isinstance(pc, Producer):
            self.producer_manager.disconnect(pc)
        else:
            self.consumer_manager.disconnect(pc)

   
            
class _ConnectionManager:
    
    """
    Connection Manager from the fastapi tutorial:
    https://fastapi.tiangolo.com/advanced/websockets/#handling-disconnections-and-multiple-clients)
    """
    
    def __init__(self):
        self.active_connections: List[PC] = []

    async def connect(self, pc: PC):
        await pc.websocket.accept()        
        self.active_connections.append(pc)
        
    def disconnect(self, pc: PC):
        self.active_connections.remove(pc)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, verbose: int = 0):
        for connection in self.active_connections:
            if connection.verbose >= verbose:
                await connection.websocket.send_text(message)

            
            