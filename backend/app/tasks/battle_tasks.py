from app.celery_app import celery
from app.redis import redis_client
import logging
import json
from datetime import datetime
import requests

from app.dtos.battles import Pokemon
from app.services.battle_engine import take_turn

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

        # Fetch pokemon HP
        # Set HP values
        pokemon1.hp = get_hp_at_level_100(pokemon1.name)
        pokemon2.hp = get_hp_at_level_100(pokemon2.name)
        
        # Simulate battle turns
        turn = 1
        while pokemon1.hp > 0 and pokemon2.hp > 0:
            attacker, defender = (pokemon1, pokemon2) if turn % 2 == 1 else (pokemon2, pokemon1)
            battle_text = take_turn(attacker, defender)
            log_message = {
                "type": "TURN",
                "turn_number": turn,
                "action": battle_text,
                "timestamp": str(datetime.now())
            }
            
            # Log to Redis
            redis_client.rpush(logs_key, json.dumps(log_message))
            
            # Update task state
            self.update_state(
                state="IN_PROGRESS",
                meta={"turn": turn, "message": log_message}
            )

            turn += 1
        
        # Final result
        winner = pokemon1.name if pokemon1.hp > 0 else pokemon2.name
        result = {
            "type": "BATTLE_END",
            "winner": winner,
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
            "winner": winner,
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


def get_hp_at_level_100(pokemon_name: str) -> int:
    # Convert name to lowercase for API
    pokemon_name = pokemon_name.lower()
    
    # Call PokeAPI
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}")
    if response.status_code == 200:
        pokemon_data = response.json()
        base_hp = next(stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'hp')
        
        # HP calculation formula at level 100:
        # ((2 * Base + IV + (EV/4)) * Level)/100 + Level + 10
        # Using 0 for IVs and EVs for simplicity
        hp_at_100 = int(((2 * base_hp + 0 + 0) * 100)/100 + 100 + 10)
        return hp_at_100
    else:
        # Default HP if API call fails
        logger.error(f"Failed to get HP for {pokemon_name} from PokeAPI")
        return 100