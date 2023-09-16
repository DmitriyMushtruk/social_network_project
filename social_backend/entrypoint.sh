#!/bin/bash

#python manage.py flush --no-input
#python manage.py migrate
python manage.py runserver 0.0.0.0:8000
celery -A social_backend worker -l info --detach
uwsgi --socket :8000 --master --enable-threads --module social_backend.wsgi

exec "$@"