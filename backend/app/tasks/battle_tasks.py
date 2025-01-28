from app.celery_app import celery
from app.redis import redis_client
import logging

logger = logging.getLogger(__name__)

@celery.task(name='app.tasks.battle_tasks.simulate_battle')
def simulate_battle(team1, team2):
    logger.info(f"Starting battle simulation with teams: {team1} vs {team2}")
    print(self.request.id)
    logs_key = f"logs:{self.request.id}"
    redis_client.delete(logs_key)  # Clear previous logs if any

    # Example battle simulation
    for turn in range(1, 6):  # Simulate 5 turns
        log_message = f"Turn {turn}: {team1[0]} attacks {team2[0]}"
        redis_client.rpush(logs_key, log_message)  # Save logs to Redis

        # Simulate some delay
        self.update_state(state="IN_PROGRESS", meta={"turn": turn, "logs": log_message})
        import time
        time.sleep(2)

    # Final result
    result_message = f"{team1[0]} wins!"
    redis_client.rpush(logs_key, result_message)
    return {"winner": team1[0], "logs": redis_client.lrange(logs_key, 0, -1)}
