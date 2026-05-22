import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from connection_manager import manager
from database import SessionLocal
from models import User
from security import SECRET_KEY, ALGORITHM

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        try:
            # Wait for the first message containing the auth token
            auth_message = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
        except asyncio.TimeoutError:
            await websocket.send_json({"error": "Auth timeout"})
            await websocket.close()
            return

        token = auth_message.get("token")
        if not token:
            await websocket.send_json({"error": "Missing token"})
            await websocket.close()
            return

        # Validate the JWT
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id_check = payload.get("sub")
            if user_id_check is None:
                await websocket.send_json({"error": "Invalid token"})
                await websocket.close()
                return
            user_id = int(user_id_check)
        except JWTError:
            await websocket.send_json({"error": "Invalid or expired token"})
            await websocket.close()
            return

        # Verify user exists
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                await websocket.send_json({"error": "User not found"})
                await websocket.close()
                return

        # Register the connection
        await manager.connect(user_id, websocket)
        await websocket.send_json({"message": "Authenticated"})

        # Keep the connection open
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(user_id)

    except WebSocketDisconnect:
        pass
