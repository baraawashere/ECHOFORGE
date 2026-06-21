"""
Keeps track of which student_id is connected on which WebSocket, so when
a new mistake triggers an analysis, we know exactly where to stream the
result. One student = one dashboard tab = one connection, in this scaffold.
"""
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, student_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[student_id] = websocket

    def disconnect(self, student_id: str) -> None:
        self._connections.pop(student_id, None)

    async def send_event(self, student_id: str, event: dict) -> None:
        """event example: {"type": "analysis_chunk", "text": "..."}"""
        websocket = self._connections.get(student_id)
        if websocket is None:
            return  # dashboard isn't open — that's fine, just skip
        await websocket.send_json(event)


manager = ConnectionManager()
