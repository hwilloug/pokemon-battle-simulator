from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.redis import redis_client
from celery.result import AsyncResult
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ws",
    tags=["ws"]
)

@router.websocket("/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    # Accept all origins for development
    # For production, replace with specific origins check
    await websocket.accept()
    try:
        logs_key = f"logs:{task_id}"
        last_index = 0
        
        while True:
            # Check if task is complete
            task_result = AsyncResult(task_id)
            if task_result.ready():
                if task_result.successful():
                    await websocket.send_json({
                        "type": "BATTLE_UPDATE",
                        "status": "COMPLETED",
                        "data": task_result.result
                    })
                else:
                    await websocket.send_json({
                        "type": "BATTLE_UPDATE",
                        "status": "FAILED",
                        "data": {"error": str(task_result.result)}
                    })
                break
            
            # Get new logs since last check
            logs = redis_client.lrange(logs_key, last_index, -1)
            if logs:
                for log in logs:
                    # Decode bytes to string before parsing JSON
                    log_str = log.decode('utf-8') if isinstance(log, bytes) else log
                    await websocket.send_json({
                        "type": "BATTLE_UPDATE",
                        "status": "IN_PROGRESS",
                        "data": json.loads(log_str)
                    })
                    last_index += 1
            
            # Add a small delay to prevent tight polling
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        logger.info(f"WebSocket connection closed for task {task_id}")
