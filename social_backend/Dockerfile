# syntax=docker/dockerfile:1

# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.10-alpine3.17

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container
RUN mkdir /project_backend

# Set the working directory to /project_backend
WORKDIR /project_backend

# Copy the current directory contents into the container at /project_backend
ADD . /project_backend/

# Install any needed packages specified in requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]