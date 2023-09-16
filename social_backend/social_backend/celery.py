from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from social_backend import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_backend.settings')

app = Celery("social_backend", broker=settings.CELERY_BROKER_URL)
app.config_from_object("django.conf.settings")

app.autodiscover_tasks()

