from __future__ import annotations
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from uuid import UUID
from app.api.deps import current_user
from app.ws.hub import hub, org_room

router = APIRouter(tags=["ws"])

@router.websocket("/ws")
async def ws_endpoint(
    websocket: WebSocket,
    token: str,                 # pass ?token=Bearer <access_token>  OR just the token string
    org_id: UUID = Query(...),  # ?org_id=<uuid>
):
    # Very small token parse: strip optional "Bearer "
    if token.lower().startswith("bearer "):
        token = token[7:]
    # Use current_user dependency-like check manually
    from app.core.security import decode_token
    try:
        payload = decode_token(token)
    except Exception:
        await websocket.close(code=4401); return

    await websocket.accept()

    room = org_room(str(org_id))
    await hub.join(room, websocket)
    try:
        # Keep the socket open; we ignore incoming client messages for now
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await hub.leave(room, websocket)
