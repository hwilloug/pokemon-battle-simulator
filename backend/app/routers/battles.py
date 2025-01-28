from fastapi import APIRouter
import logging
from celery.result import AsyncResult
from app.tasks.battle_tasks import simulate_battle
from app.celery_app import celery

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/battles",
    tags=["battles"]
)


@router.get("/start")
async def start_battle():
    logger.info("Attempting to start battle simulation...")
    try:
        # Test broker connection
        conn = celery.connection()
        conn.connect()
        logger.info("Successfully connected to broker")
        
        # Send task
        task = simulate_battle.delay(team1={"name": "Team 1"}, team2={"name": "Team 2"})
        logger.info(f"Task sent with ID: {task.id}")
        
        # Get task status immediately after creation
        task_result = AsyncResult(task.id)
        return {
            "task_id": task.id,
            "task_status": task_result.status,
            "task_state": task_result.state
        }
    except Exception as e:
        logger.error(f"Error starting battle: {e}", exc_info=True)
        raise

@router.get("/{id}/stop")
async def stop_battle(id: int):
    return {"message": f"Battle {id} stopped"}


@router.get("/{id}")
async def get_battle(id: int):
    return {"message": f"Battle {id} started"}


@router.get("/{id}/status")
async def get_battle_status(id: int):
    return {"message": f"Battle {id} status"}


@router.get("/{id}/log")
async def get_battle_log(id: int):
    return {"message": f"Battle {id} log"}
