import json
import logging.config
import socket

import pika

from social_backend.celery import app
from social_backend import settings
from kombu.exceptions import OperationalError


@app.task(name="send_message", queue="stats")
def send_message(method, body):
    connection = pika.BlockingConnection(pika.URLParameters(settings.CELERY_BROKER_URL))
    channel = connection.channel()

    channel.queue_declare(queue='stats')
    properties = pika.BasicProperties(method)

    message_data = {
        "method": method,
        "body": body
    }

    channel.basic_publish(
        exchange='',
        routing_key='stats',
        body=json.dumps(message_data),
        properties=properties
    )
    connection.close()
