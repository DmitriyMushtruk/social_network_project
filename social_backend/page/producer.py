import json
import logging.config
import socket

import pika

from social_backend.celery import app
from social_backend import settings
from kombu.exceptions import OperationalError


@app.task(name="send_message", queue="hello")
def send_message(method, body):
    connection = pika.BlockingConnection(pika.URLParameters(settings.CELERY_BROKER_URL))
    channel = connection.channel()

    channel.queue_declare(queue='hello')
    properties = pika.BasicProperties(method)

    channel.basic_publish(
        exchange='',
        routing_key='hello',
        body=json.dumps(body),
        properties=properties
    )
    connection.close()

