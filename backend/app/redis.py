
from redis import Redis


redis_client = Redis(
    host='redis',
    port=6379,
    db=0,
    decode_responses=True
)

try:
    redis_client.ping()
    print("Successfully connected to Redis")
except Exception as e:
    print(f"Failed to connect to Redis: {e}")
