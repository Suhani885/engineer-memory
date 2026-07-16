# Engineering Memory

Engineering Memory is the future memory layer for engineering teams. This repository currently contains only the production-oriented application scaffold; product features have deliberately not been implemented.

## Architecture

```text
frontend/                 Next.js 15 application
backend/app/
  api/                    HTTP delivery layer
  workers/                Celery application and future jobs
  github/                 GitHub integration boundary
  ai/                     AI provider boundary
  parser/                 Change parsing boundary
  models/                 SQLAlchemy persistence models
  services/               Application use cases
  repositories/           Data access abstractions
  core/                   Configuration, database, logging
infra/postgres/           Database bootstrap scripts
```

Dependencies flow inward: API endpoints and workers call services; services use repositories and integration boundaries; models and core provide persistence and platform concerns. Domain capabilities will be added in later iterations.

## Prerequisites

- Docker Desktop with Docker Compose v2
- Node.js 20+ and Python 3.12+ only when running services outside Docker

## Run locally

1. Copy the environment template: `cp .env.example .env`
2. Update the placeholder secrets in `.env`.
3. Start the production-style stack: `docker compose up --build`
4. Apply migrations when domain models are introduced: `make migrate`

The frontend is available at `http://localhost:3000`; the API health check is at `http://localhost:8000/health`.

For hot reload and the development toolchain, run `make dev`. It layers `compose.dev.yaml` over the production Compose definition.

## Development commands

```bash
make up
make dev
make down
make logs
make lint
make test
```

## Initial scope

This scaffold includes configuration, containerization, PostgreSQL with pgvector, Redis, Celery, FastAPI, Alembic, and a minimal Next.js shell. It does not yet implement GitHub ingestion, change understanding, knowledge storage, search, timelines, or an AI advisor.
