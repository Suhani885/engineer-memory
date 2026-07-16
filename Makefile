.DEFAULT_GOAL := help

.PHONY: help up dev down logs migrate revision test lint format

help:
	@echo "Available targets: up dev down logs migrate revision test lint format"

up:
	docker compose up --build

dev:
	docker compose -f compose.yaml -f compose.dev.yaml up --build

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose run --rm api alembic upgrade head

revision:
	docker compose run --rm api alembic revision --autogenerate -m "$(message)"

test:
	docker compose -f compose.yaml -f compose.dev.yaml run --rm api pytest

lint:
	docker compose -f compose.yaml -f compose.dev.yaml run --rm api ruff check .
	docker compose -f compose.yaml -f compose.dev.yaml run --rm frontend npm run lint

format:
	docker compose -f compose.yaml -f compose.dev.yaml run --rm api ruff format .
	docker compose -f compose.yaml -f compose.dev.yaml run --rm frontend npm run format
