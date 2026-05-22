from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Maps user id to their WebSocket connection
        self.connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        self.connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.connections:
            del self.connections[user_id]

    async def send_to_user(self, user_id: int, message: dict):
        if user_id in self.connections:
            try:
                await self.connections[user_id].send_json(message)
            except Exception:
                # Connection did not work, remove user
                self.disconnect(user_id)

    async def broadcast(self, message: dict):
        # Send to all connected users
        failed_connections = []
        for user_id, ws in self.connections.items():
            try:
                await ws.send_json(message)
            except Exception:
                failed_connections.append(user_id)

        # Clean up failed connections
        for user_id in failed_connections:
            self.disconnect(user_id)


manager = ConnectionManager()
