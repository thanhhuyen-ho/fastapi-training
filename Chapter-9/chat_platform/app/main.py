import logging

from fastapi import FastAPI, WebSocket, status, WebSocketException, Depends
from fastapi.websockets import WebSocketDisconnect

from typing import Annotated

from app.chat import router as chat_router
from app.security import get_username_from_token, router as security_router
from app.private_chatroom import router as private_chatroom_router

app = FastAPI()
app.include_router(chat_router)
app.include_router(private_chatroom_router)
app.include_router(security_router)

logger = logging.getLogger("uvicorn")

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Welcome to the chat room!")
    # await websocket.close()
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Message received: {data}")
            await websocket.send_text("Message received")
            if data == "disconnect":
                logger.warn("Disconnecting ...")
                await websocket.close(
                    code=status.WS_1000_NORMAL_CLOSURE,
                    reason="Disconnecting..."
                )
            if "bad message" in data:
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Inappropriate message",
                )
    except WebSocketDisconnect:
        logger.warning("Connection closed by the client.")
        
@app.websocket("/secured-ws")
async def secured_websocket(
    websocket: WebSocket, 
    username: Annotated[
        get_username_from_token, 
        Depends()
    ]
):
    await websocket.accept()
    await websocket.send_text(f"Welcome {username}!")
    async for data in websocket.iter_text():
        await websocket.send_text(
            f"Your wrote: {data}"
        )