from app.celery_app import celery

# This is just to make sure all tasks are imported and registered
import app.tasks.battle_tasks

# Export the celery app for the worker
app = celery

if __name__ == '__main__':
    celery.start() 