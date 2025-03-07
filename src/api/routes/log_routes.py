"""
Log routes for the API.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any
import asyncio
import queue
import threading
import time
from utils.logging import get_recent_logs, get_user_logs, log_event, info, debug, error

router = APIRouter()

# Store active WebSocket connections
active_connections: List[WebSocket] = []
# Global queue for log messages
log_queue = queue.Queue()

# Background thread to process synchronous queue and distribute to websockets
def start_queue_processor():
    """Process messages from the queue and distribute to all WebSocket connections."""
    async def send_to_websockets(log_entry):
        # Make a copy to avoid concurrent modification issues
        connections = list(active_connections)
        if connections:
            debug(f"LOG - Sending to {len(connections)} clients: {log_entry['message'][:30]}...")
        
        for websocket in connections:
            try:
                await websocket.send_json({"type": "log", "log": log_entry})
            except Exception as e:
                error(f"LOG - WebSocket send error: {str(e)}")
                # Connection probably closed, will be removed later
                pass
    
    info("LOG - Starting distributor thread")
    while True:
        try:
            # Get log from queue (blocks until an item is available)
            log_entry = log_queue.get()
            
            # If we have connections, create a task to send the message
            if active_connections:
                # Create an event loop for async operations
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # Run until complete
                    loop.run_until_complete(send_to_websockets(log_entry))
                finally:
                    loop.close()
            
            # Mark item as processed
            log_queue.task_done()
        except Exception as e:
            error(f"LOG - Queue processing error: {str(e)}")
            # Sleep briefly to avoid tight loops in case of persistent errors
            time.sleep(0.1)

# Start the background thread for queue processing
queue_thread = threading.Thread(target=start_queue_processor, daemon=True)
queue_thread.start()

# Setup signal receiver for new logs - must be synchronous
def handle_log(sender, **kwargs):
    """Handle new log events synchronously."""
    log_entry = kwargs.get('log_entry', sender)
    # Add to synchronous queue
    log_queue.put(log_entry)
    debug(f"LOG - Queued: {log_entry['message'][:30]}...")

# Register the signal handler
log_event.connect(handle_log)
info("LOG - Event handler registered")

@router.get("/logs")
async def get_logs(user_only: bool = False, count: int = 100):
    """Get recent logs."""
    if user_only:
        logs = get_user_logs()[:count]
        debug(f"LOG - Returning {len(logs)} user logs")
        return logs
    else:
        logs = get_recent_logs()[:count]
        debug(f"LOG - Returning {len(logs)} system logs")
        return logs

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time log updates."""
    client_info = f"{websocket.client.host}:{websocket.client.port}"
    info(f"LOG - New connection from {client_info}")
    
    await websocket.accept()
    active_connections.append(websocket)
    info(f"LOG - Connection accepted: {len(active_connections)} active")
    
    # Send initial logs
    initial_logs = get_user_logs()
    info(f"LOG - Sending {len(initial_logs)} initial logs")
    await websocket.send_json({"type": "initial", "logs": initial_logs})
    
    try:
        # Keep the WebSocket connection alive
        while True:
            # Wait for any message from the client (can be a heartbeat)
            data = await websocket.receive_text()
            # You could process client messages here if needed
            if data == "ping":
                await websocket.send_text("pong")
                debug(f"LOG - Ping received from {client_info}")
    except WebSocketDisconnect:
        # Remove connection when disconnected
        if websocket in active_connections:
            active_connections.remove(websocket)
            info(f"LOG - Client disconnected: {len(active_connections)} remaining")
    
    # Return after disconnection
    return 