"""
Log routes for the API.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import json
from utils.logging import get_recent_logs, get_user_logs, log_event

router = APIRouter()

# Store active WebSocket connections
active_connections: List[WebSocket] = []

@router.get("/logs")
async def get_logs(user_only: bool = False, count: int = 100):
    """Get recent logs."""
    if user_only:
        return get_user_logs()[:count]
    else:
        return get_recent_logs()[:count]

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time log updates."""
    await websocket.accept()
    active_connections.append(websocket)
    
    # Send initial logs
    initial_logs = get_user_logs()
    await websocket.send_json({"type": "initial", "logs": initial_logs})
    
    # Setup signal receiver for new logs
    def handle_log(sender, **kwargs):
        log_entry = kwargs.get('log_entry', sender)
        for conn in active_connections:
            try:
                # Use run_until_complete to run the coroutine in a synchronous context
                import asyncio
                asyncio.create_task(conn.send_json({"type": "log", "log": log_entry}))
            except Exception:
                # We'll clean up failed connections in the main loop
                pass
    
    # Register the signal handler
    log_event.connect(handle_log)
    
    try:
        # Keep the WebSocket connection alive
        while True:
            # Wait for any message from the client (can be a heartbeat)
            data = await websocket.receive_text()
            # You could process client messages here if needed
    except WebSocketDisconnect:
        # Remove connection when disconnected
        active_connections.remove(websocket)
        # Disconnect signal handler to avoid memory leaks
        log_event.disconnect(handle_log) 