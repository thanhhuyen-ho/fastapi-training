from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, WebSocketDisconnect, WebSocket, Depends, Request
from fastapi.responses import  RedirectResponse
from typing import Annotated
from app.ws_manager import ConnectionManager
from app.security import fake_token_resolver, get_username_from_token


conn_manager = ConnectionManager()

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/private-chatroom")
async def private_chatroom_page_endpoint(
    request: Request
):
    token = request.cookies.get("chatroomtoken")
    if not token:
        return RedirectResponse(
            url="/login?redirecturl=http://localhost:8000/private-chatroom",
        )
    
    user = fake_token_resolver(token)
    if not user:
        return RedirectResponse(
            url="/login?redirecturl=http://localhost:8000/private-chatroom",
        )
    return templates.TemplateResponse(
        request=request,
        name="chatroom.html",
        context={"username": user.username},
    )

@router.websocket("/ws-private-chatroom")
async def private_chatroom_endpoint(
    websocket: WebSocket,
    username: Annotated[
        get_username_from_token, Depends()
    ],
):
    await conn_manager.connect(websocket)
    await conn_manager.broadcast(
        {
            "sender": "system",
            "message": f"{username} joined the chat",
        },
        exclude=websocket,
    )
    try:
        while True:
            data = await websocket.receive_text()
            await conn_manager.broadcast(
                {"sender": username, "message": data},
                exclude=websocket
            )
            await conn_manager.send_personal_message(
                {"sender": "You", "message":data},
                websocket
            )
    except WebSocketDisconnect:
        conn_manager.disconnect(websocket)
        await conn_manager.broadcast(
            {
                "sender": "system",
                "message": f"client #{username} "
                "left the private chat"
            }
        )
        