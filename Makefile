# Makefile

# Commands for linting and formatting
lint:
	pylint --load-plugins pylint_django social_backend
	black social_backend
	isort social_backend

# Command to build and run Docker container
docker:
	docker-compose up -d --build

# Command to run tests
test:
	docker exec -it 85f6912bc133 pytest

# Default target
default: lint docker test