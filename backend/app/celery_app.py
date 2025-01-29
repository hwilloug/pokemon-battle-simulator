import os
from celery import Celery
from redis import Redis
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get broker and backend URLs from environment variables
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

print(f"Using broker URL: {CELERY_BROKER_URL}")
print(f"Using result backend: {CELERY_RESULT_BACKEND}")

# Add connection logging
logger.debug(f"Attempting to connect to broker at: {CELERY_BROKER_URL}")
logger.debug(f"Attempting to connect to backend at: {CELERY_RESULT_BACKEND}")

celery = Celery(
    "pokemon_battle_simulator",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Test broker connection
try:
    conn = celery.connection()
    conn.connect()
    logger.info("Successfully connected to the broker!")
except Exception as e:
    logger.error(f"Failed to connect to the broker: {e}")

# Update imports to include the tasks subfolder
celery.conf.update(
    imports=[
        'app.tasks.battle_tasks',
        'app.tasks.health_tasks'
    ],
    task_routes={
        'app.tasks.*': {'queue': 'default'}
    },
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
    worker_concurrency=1,
    task_always_eager=False,
    task_acks_late=True,
)

# Add these debug lines after the conf.update
logger.info("Celery Configuration:")
logger.info(f"Broker URL: {celery.conf.broker_url}")
logger.info(f"Result Backend: {celery.conf.result_backend}")
logger.info(f"Task Routes: {celery.conf.task_routes}")
logger.info("Available Tasks:")
for task_name in sorted(celery.tasks.keys()):
    logger.info(f"- {task_name}")

# Test broker connection again after configuration
try:
    conn = celery.connection()
    conn.connect()
    logger.info("Successfully connected to the broker!")
    conn.release()
except Exception as e:
    logger.error(f"Failed to connect to the broker: {e}")