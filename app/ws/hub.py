from __future__ import annotations
from typing import Dict,Set
from starlette.websockets import WebSocket
import json
import asyncio

class Hub:
    def __init__(self):
        self.rooms: Dict[str, Set[WebSocket]] = {}
        self.lock = asyncio.Lock()

    async def join(self,room:str,ws: WebSocket):
        async with self.lock:
            self.rooms.setdefault(room,set()).add(ws)

    async def leave(self,room: str, ws:WebSocket):
        async with self.lock:
            if room in self.rooms and ws in self.rooms[room]:
                self.rooms[room].remove(ws)
            if room in self.rooms and not self.rooms[room]:
                self.rooms.pop(room,None)

    async def broadcast(self, room: str, event: dict):
        # Copy to avoid concurrent modification
        targets: list[WebSocket] = []
        async with self.lock:
            for ws in self.rooms.get(room, set()):
                targets.append(ws)
        if not targets:
            return
        msg = json.dumps(event)
        to_drop = []
        for ws in targets:
            try:
                await ws.send_text(msg)
            except Exception:
                to_drop.append(ws)
        if to_drop:
            async with self.lock:
                for ws in to_drop:
                    for r, members in list(self.rooms.items()):
                        if ws in members:
                            members.remove(ws)
                            if not members:
                                self.rooms.pop(r, None)

hub = Hub()
def org_room(org_id: str) -> str:
    return f"org:{org_id}"
