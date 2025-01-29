from app.celery_app import celery
import logging

logger = logging.getLogger(__name__)

@celery.task(name='app.tasks.health_tasks.health_check', bind=True)
def health_check(self):
    task_id = self.request.id
    logger.info(f"Executing health check task with ID: {task_id}")
    
    # Add some status updates to verify task execution
    self.update_state(state='PROGRESS', meta={'status': 'Health check in progress'})
    
    # Simulate some work
    import time
    time.sleep(2)
    
    result = "Health check completed successfully"
    logger.info(f"Task {task_id}: {result}")
    return result 