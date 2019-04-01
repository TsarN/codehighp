import os
from celery import Celery

app = Celery('codehighp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
