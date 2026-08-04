"""WebSocket endpoints: live price streaming + prediction progress."""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.ws.hub import get_hub

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/prices")
async def ws_prices(websocket: WebSocket):
    await websocket.accept()
    hub = get_hub()
    asset = websocket.query_params.get("asset", "BTC")
    await hub.subscribe(websocket, asset)
    try:
        while True:
            # client may send a new subscription
            message = await websocket.receive_text()
            if message.startswith("subscribe:"):
                new_asset = message.split(":", 1)[1].strip()
                await hub.subscribe(websocket, new_asset)
    except WebSocketDisconnect:
        pass
    finally:
        await hub.unsubscribe(websocket)
