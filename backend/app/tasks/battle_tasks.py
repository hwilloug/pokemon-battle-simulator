from app.celery_app import celery
from app.redis import redis_client
import logging
import json
import time
from datetime import datetime

from app.dtos.battles import Pokemon

logger = logging.getLogger(__name__)

@celery.task(name='app.tasks.battle_tasks.simulate_battle', bind=True)
def simulate_battle(self, pokemon1_data: dict, pokemon2_data: dict):
    task_id = self.request.id
    logger.info(f"Starting battle simulation task {task_id}")
    
    # Convert dictionary data to Pokemon objects
    pokemon1 = Pokemon(**pokemon1_data)
    pokemon2 = Pokemon(**pokemon2_data)
    
    logs_key = f"logs:{task_id}"
    redis_client.delete(logs_key)  # Clear previous logs if any
    
    try:
        # Initial battle state
        redis_client.rpush(logs_key, json.dumps({
            "type": "BATTLE_START",
            "pokemon1": pokemon1.name,
            "pokemon2": pokemon2.name,
            "timestamp": str(datetime.now())
        }))
        
        # Simulate battle turns
        for turn in range(1, 6):
            # Simulate battle logic
            log_message = {
                "type": "TURN",
                "turn_number": turn,
                "action": f"{pokemon1.name} attacks {pokemon2.name}",
                "timestamp": str(datetime.now())
            }
            
            # Log to Redis
            redis_client.rpush(logs_key, json.dumps(log_message))
            
            # Update task state
            self.update_state(
                state="IN_PROGRESS",
                meta={"turn": turn, "message": log_message}
            )
            
            # Simulate battle delay
            time.sleep(2)
        
        # Final result
        result = {
            "type": "BATTLE_END",
            "winner": pokemon1.name,
            "timestamp": str(datetime.now())
        }
        redis_client.rpush(logs_key, json.dumps(result))
        
        # Include winner in the completed state
        self.update_state(
            state="COMPLETED",
            meta=result
        )
        
        return {
            "status": "COMPLETED",
            "winner": pokemon1.name,
            "logs": [json.loads(log) for log in redis_client.lrange(logs_key, 0, -1)]
        }
        
    except Exception as e:
        error_msg = {
            "type": "error",
            "message": str(e),
            "timestamp": str(datetime.now())
        }
        redis_client.rpush(logs_key, json.dumps(error_msg))
        raise
