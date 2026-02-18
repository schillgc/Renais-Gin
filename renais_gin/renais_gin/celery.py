"""
Celery configuration for Renais Gin project.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'renais_gin.settings')

# Create Celery app instance
app = Celery('renais_gin')

# Configure Celery using settings from Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps
app.autodiscover_tasks()

# Optional configuration for better task handling
app.conf.update(
    # Task result expires after 1 hour
    result_expires=3600,

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,

    # Task routes (if needed)
    task_routes={
        'core.tasks.process_rebate_payments': {'queue': 'payments'},
        'core.tasks.send_pledge_status_notification': {'queue': 'notifications'},
        'core.tasks.send_weekly_newsletter': {'queue': 'notifications'},
        'core.tasks.update_movement_metrics': {'queue': 'metrics'},
        'core.tasks.update_user_engagement_scores': {'queue': 'metrics'},
        'core.tasks.cleanup_old_data': {'queue': 'maintenance'},
        'core.tasks.generate_daily_reports': {'queue': 'reports'},
    },

    # Beat schedule for periodic tasks
    beat_schedule={
        # Update metrics every hour
        'update-movement-metrics-hourly': {
            'task': 'core.tasks.update_movement_metrics',
            'schedule': 3600.0,  # 1 hour in seconds
        },

        # Process pending validations every 30 minutes
        'process-pending-validations': {
            'task': 'core.tasks.process_pending_validations',
            'schedule': 1800.0,  # 30 minutes
        },

        # Process rebate payments daily at 2 AM
        'process-rebate-payments-daily': {
            'task': 'core.tasks.process_rebate_payments',
            'schedule': 86400.0,  # 24 hours
            # For specific time scheduling, use crontab:
            # 'schedule': crontab(hour=2, minute=0),
        },

        # Update engagement scores daily at 3 AM
        'update-engagement-scores-daily': {
            'task': 'core.tasks.update_user_engagement_scores',
            'schedule': 86400.0,
        },

        # Cleanup old data weekly on Sunday at 4 AM
        'cleanup-old-data-weekly': {
            'task': 'core.tasks.cleanup_old_data',
            'schedule': 604800.0,  # 7 days
        },

        # Send weekly newsletter every Monday at 9 AM
        'send-weekly-newsletter': {
            'task': 'core.tasks.send_weekly_newsletter',
            'schedule': 604800.0,
        },

        # Generate daily reports at 6 AM
        'generate-daily-reports': {
            'task': 'core.tasks.generate_daily_reports',
            'schedule': 86400.0,
        },
    },

    # Timezone settings
    timezone='UTC',

    # Enable task events for monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Debug task to test Celery worker functionality.
    """
    print(f'[Celery] Request: {self.request!r}')
    return f'Hello from Celery! Task ID: {self.request.id}'


@app.task(bind=True)
def health_check(self):
    """
    Health check task for monitoring Celery workers.
    """
    return {
        'status': 'healthy',
        'worker': self.request.hostname,
        'timestamp': self.request.timestamp,
    }


# Error handling for task failures
@app.task(bind=True)
def handle_task_failure(self, exc, task_id, args, kwargs, einfo):
    """
    Global task failure handler.
    """
    print(f'Task {task_id} failed: {exc}')
    # Here you could send notifications, log to monitoring service, etc.

    # Example: Send to error tracking service
    # from .services import ErrorTrackingService
    # ErrorTrackingService().capture_exception(exc)


# Task base class with common functionality
class RenaisGinTask(app.Task):
    """
    Base task class for Renais Gin with common error handling and logging.
    """

    abstract = True  # This is a base class, not a concrete task

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Handle task failures.
        """
        print(f'❌ Task {self.name} failed: {exc}')
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """
        Handle task successes.
        """
        print(f'✅ Task {self.name} completed successfully')
        super().on_success(retval, task_id, args, kwargs)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """
        Handle task retries.
        """
        print(f'🔄 Task {self.name} retrying: {exc}')
        super().on_retry(exc, task_id, args, kwargs, einfo)


# Make base task class available
app.Task = RenaisGinTask

if __name__ == '__main__':
    """
    Allow running this file directly for debugging Celery.
    """
    app.start()
