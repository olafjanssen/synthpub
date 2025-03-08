"""
Log routes for the API.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import asyncio
import time
from contextlib import asynccontextmanager
from utils.logging import get_recent_logs, info, debug
from api.signals import log_event as log_signal

router = APIRouter()

# Store active WebSocket connections
active_connections: List[WebSocket] = []

# Keep track of the main event loop
main_event_loop = None

# Handler for log events
def handle_log(sender, **kwargs):
    """Handle log event from the signal system."""
    # Extract log data
    log_data = kwargs.get('log_entry', {})
    
    # Add timestamp if not present
    if 'timestamp' not in log_data:
        log_data['timestamp'] = time.time()
    
    # Only send logs with minimum level INFO
    log_level = log_data.get('level', '').upper()
    if log_level not in ('INFO', 'WARNING', 'WARN', 'ERROR', 'CRITICAL'):
        return
    
    # Send log to all active websocket connections
    if main_event_loop is not None and not main_event_loop.is_closed():
        try:
            # Make a copy to avoid concurrent modification issues
            connections = list(active_connections)
            
            for websocket in connections:
                asyncio.run_coroutine_threadsafe(
                    send_log_to_websocket(websocket, log_data),
                    main_event_loop
                )
        except Exception as e:
            print(f"Error sending log: {e}")
    else:
        # Fallback - log to console only
        print(f"Log event without event loop: {log_data}")

async def send_log_to_websocket(websocket: WebSocket, log_data: Dict[str, Any]):
    """Send a log entry to a specific websocket."""
    try:
        await websocket.send_json({"type": "log", "log": log_data})
    except Exception as e:
        debug("WEBSOCKET", "Send failed", str(e))
        # Connection probably closed, remove it
        if websocket in active_connections:
            active_connections.remove(websocket)

@router.get("/logs")
async def get_logs(min_level: str = "INFO", count: int = 100):
    """Return recent logs."""
    logs = get_recent_logs(min_level=min_level, max_count=count)
    return logs

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time log updates."""
    global main_event_loop
    
    # Store the main event loop for later use
    if main_event_loop is None:
        main_event_loop = asyncio.get_running_loop()
    
    client_info = f"{websocket.client.host}:{websocket.client.port}"
    debug("WEBSOCKET", "New connection", client_info)
    
    await websocket.accept()
    active_connections.append(websocket)
    debug("WEBSOCKET", "Connection accepted", f"{len(active_connections)} active connections")
    
    # Send initial logs
    initial_logs = get_recent_logs(min_level="INFO", max_count=50)
    debug("WEBSOCKET", "Sending initial logs", f"{len(initial_logs)} logs to {client_info}")
    await websocket.send_json({"type": "initial", "logs": initial_logs})
    
    try:
        # Keep the WebSocket connection alive
        while True:
            # Wait for any message from the client (can be a heartbeat)
            data = await websocket.receive_text()
            # You could process client messages here if needed
            if data == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time()})
    except WebSocketDisconnect:
        debug("WEBSOCKET", "Client disconnected", client_info)
        # Remove from the active connections
        if websocket in active_connections:
            active_connections.remove(websocket)
        debug("WEBSOCKET", "Client disconnected", f"{len(active_connections)} connections remaining")

# Define lifespan for this router
@asynccontextmanager
async def lifespan(app):
    # Startup: register log handler
    global main_event_loop
    main_event_loop = asyncio.get_running_loop()
    log_signal.connect(handle_log)
    debug("SYSTEM", "Starting WebSocket distributor", "Log message relay")
    yield
    
    # Shutdown: cleanup if needed
    log_signal.disconnect(handle_log)

# Expose lifespan to be used by the main application
router.lifespan = lifespan