import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_aggregator.settings')

app = Celery('news_aggregator')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix in settings.py.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery Beat Scheduler Configuration (This replaces the cron job)
# System Action: Scheduler/Cron Job is triggered (e.g., every 30 minutes).
app.conf.beat_schedule = {
    'run-scraping-flow-every-30-minutes': {
        'task': 'aggregator.tasks.start_scraping_flow',
        'schedule': 1800.0, # Run every 30 minutes (1800 seconds)
        'args': (),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')