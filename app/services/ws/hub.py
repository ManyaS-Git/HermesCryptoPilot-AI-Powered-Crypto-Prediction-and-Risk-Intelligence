"""Real-time price streaming hub.

Connects to Binance's public websocket stream and fans out trade/ticker
updates to subscribed API clients over FastAPI WebSockets. Connection errors
reconnect with backoff; no synthetic data is ever emitted.
"""
from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict

import websockets

from app.services.market.symbols import usdt_pair

logger = logging.getLogger(__name__)

BINANCE_WS = "wss://stream.binance.com:9443/ws"


class PriceStreamHub:
    def __init__(self) -> None:
        self._subscribers: dict[str, set] = defaultdict(set)  # asset -> websockets
        self._asset_subscriptions: set[str] = set()
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        self._last_price: dict[str, float] = {}

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def subscribe(self, websocket, asset: str) -> None:
        async with self._lock:
            self._subscribers[asset.upper()].add(websocket)
            self._asset_subscriptions.add(asset.upper())
            await self._rebuild_stream()
        # send a snapshot of the last known price if available
        if asset.upper() in self._last_price:
            await self._send(
                websocket,
                {"type": "price", "asset": asset.upper(), "price": self._last_price[asset.upper()], "snapshot": True},
            )

    async def unsubscribe(self, websocket, asset: str | None = None) -> None:
        async with self._lock:
            if asset:
                self._subscribers[asset.upper()].discard(websocket)
                if not self._subscribers[asset.upper()]:
                    self._asset_subscriptions.discard(asset.upper())
            else:
                for asset_set in self._subscribers.values():
                    asset_set.discard(websocket)
                assets_to_remove = [a for a, s in self._subscribers.items() if not s]
                for a in assets_to_remove:
                    self._subscribers.pop(a, None)
                    self._asset_subscriptions.discard(a)
            await self._rebuild_stream()

    async def _rebuild_stream(self) -> None:
        assets = sorted(self._asset_subscriptions)
        if not assets:
            return
        streams = "/".join(f"{usdt_pair(a).lower()}@trade" for a in assets)
        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
            self._ws = None
        self._ws = await websockets.connect(f"{BINANCE_WS}/{streams}", ping_interval=20)

    async def _run(self) -> None:
        while True:
            try:
                if not self._asset_subscriptions:
                    await asyncio.sleep(0.5)
                    continue
                if self._ws is None:
                    await self._rebuild_stream()
                    continue
                message = await asyncio.wait_for(self._ws.recv(), timeout=30)
                data = json.loads(message)
                await self._dispatch(data)
            except asyncio.TimeoutError:
                continue
            except Exception as exc:  # noqa: BLE001
                logger.warning("Price stream error: %s", exc)
                self._ws = None
                await asyncio.sleep(2)

    async def _dispatch(self, data: dict) -> None:
        if data.get("e") != "trade":
            return
        symbol = (data.get("s") or "").replace("USDT", "")
        if not symbol:
            return
        price = float(data.get("p", 0))
        self._last_price[symbol] = price
        payload = json.dumps(
            {"type": "price", "asset": symbol, "price": price, "qty": float(data.get("q", 0))}
        )
        for ws in list(self._subscribers.get(symbol, ())):
            await self._send(ws, payload)

    @staticmethod
    async def _send(websocket, message: str | dict) -> None:
        try:
            payload = message if isinstance(message, str) else json.dumps(message)
            await websocket.send_text(payload)
        except Exception:
            pass


_hub: PriceStreamHub | None = None


def get_hub() -> PriceStreamHub:
    global _hub
    if _hub is None:
        _hub = PriceStreamHub()
    return _hub
