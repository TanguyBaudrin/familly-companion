.PHONY: help install run docker-build docker-run clean

help:
	@echo "Commands:"
	@echo "  install       : Install dependencies using uv."
	@echo "  run           : Run the application."
	@echo "  docker-build  : Build the docker image."
	@echo "  docker-run    : Run the docker container."
	@echo "  clean         : Clean all build artifacts."

install:
	uv sync

run:
	uv run uvicorn src.main:app --reload

db-migrate:
	uv run alembic upgrade head

docker-build:
	docker build -t familly-companion .

docker-run:
	docker run -p 80:80 familly-companion

clean:
	rm -rf .venv
	rm -rf .pytest_cache
	rm -rf .coverage
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
