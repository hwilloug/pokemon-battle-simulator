import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.routers import battles, status
from app.redis import redis_client
from celery.result import AsyncResult

app = FastAPI(
    title="Pokemon Battle Simulator",
    description="A Pokemon battle simulator API",
    version="0.1.0"
)

app.include_router(battles.router)
app.include_router(status.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/{task_id}")
async def battle_ws(websocket: WebSocket, task_id: str):
    await websocket.accept()
    try:
        while True:
            # Check task status
            result = AsyncResult(task_id)
            status = result.status

            # Retrieve logs or updates from Redis
            logs = redis_client.lrange(f"logs:{task_id}", 0, -1)

            # Send updates to the WebSocket client
            await websocket.send_json({"status": status, "logs": logs})

            # Break the loop if the task is complete
            if result.ready():
                break

            # Wait before checking again
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for task {task_id}")