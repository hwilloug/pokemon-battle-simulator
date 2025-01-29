from fastapi import APIRouter, Body
import logging
from celery.result import AsyncResult
from app.tasks.battle_tasks import simulate_battle
from app.celery_app import celery
from app.tasks.health_tasks import health_check

from app.dtos.battles import StartBattleDTO
from app.dtos.tasks import TaskStatus

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/battles",
    tags=["battles"]
)

@router.post("/start")
async def start_battle(
    start_battle_dto: StartBattleDTO
) -> TaskStatus:
    logger.info(f"Attempting to start battle simulation with body: {start_battle_dto}")
    try:
        # Test broker connection
        conn = celery.connection()
        conn.connect()
        logger.info("Successfully connected to broker")
        
        # Convert Pokemon objects to dictionaries before sending
        pokemon1_dict = start_battle_dto.pokemon1.model_dump()
        pokemon2_dict = start_battle_dto.pokemon2.model_dump()
        
        # Send task with serialized data
        task = simulate_battle.apply_async(
            args=[pokemon1_dict, pokemon2_dict]
        )
        logger.info(f"Task sent with ID: {task.id}")
        
        # Get task status immediately after creation
        task_result = AsyncResult(task.id)
        return TaskStatus(
            task_id=task.id,
            status=task_result.status
        )
    except Exception as e:
        logger.error(f"Error starting battle: {e}", exc_info=True)
        raise
