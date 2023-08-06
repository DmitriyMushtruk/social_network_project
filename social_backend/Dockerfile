# syntax=docker/dockerfile:1

# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.10-alpine3.17

ARG DJANGO_ENV

ENV DJANGO_ENV=${DJANGO_ENV} \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.5.1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry'

  RUN apk update && apk add nmap-ncat

  RUN apk --update add bash && \
      apk add dos2unix

RUN pip install "poetry==$POETRY_VERSION" && poetry --version
RUN pip install python-dotenv

# Set the working directory to /project_backend
WORKDIR /project_backend

COPY pyproject.toml /project_backend
COPY poetry.lock /project_backend

# Install dependencies:
RUN poetry install --no-root

# Copy entrypoint.sh
COPY entrypoint.sh /project_backend
RUN sed -i 's/\r$//g' /project_backend/entrypoint.sh
RUN chmod +x /project_backend/entrypoint.sh

# Copy the current directory contents into the container at /project_backend
COPY . .

# Run entrypoint.sh
ENTRYPOINT ["/project_backend/entrypoint.sh"]