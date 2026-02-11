import time
from celery import shared_task

@shared_task(bind=True, max_retries=0)
def io_bound_task(self, duration=5):
    time.sleep(duration)
    return {"task_id": self.request.id, "duration": duration}

@shared_task
def generate_load(count=20, duration=30):
    for _ in range(count):
        io_bound_task.delay(duration=duration)
    return {"dispatched": count}
