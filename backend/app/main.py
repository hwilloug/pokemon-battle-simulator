import asyncio
from app.routers import ws
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.routers import battles

app = FastAPI(
    title="Pokemon Battle Simulator",
    description="A Pokemon battle simulator API",
    version="0.1.0"
)

app.include_router(battles.router)
app.include_router(ws.router)

origins = ["*"]  # In production, replace with specific origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
