# Engineering Memory

> **The memory layer for engineering teams.**
> Capture, understand, and search your engineering knowledge automatically — across GitHub PRs, deployments, documentation, and team discussions.

---

## Architecture

```
engineer-memory/
├── backend/                  FastAPI application (Python 3.12)
│   └── app/
│       ├── api/              HTTP layer (routes, deps, schemas)
│       │   └── v1/
│       │       ├── auth.py
│       │       ├── organizations.py
│       │       └── schemas/
│       ├── core/             Cross-cutting concerns
│       │   ├── config.py     Pydantic-settings (env vars)
│       │   ├── db.py         SQLAlchemy engine + session
│       │   └── security.py   JWT (HS256) + bcrypt helpers
│       ├── models/           SQLAlchemy ORM models
│       │   ├── organization.py
│       │   ├── user.py
│       │   └── membership.py
│       ├── repositories/     Data access layer (org-scoped)
│       ├── services/         Business logic
│       ├── workers/          Celery tasks (async processing)
│       ├── ai/               AI / OpenAI integration (future)
│       ├── github/           GitHub App integration (future)
│       └── parser/           Code/diff parsing (future)
│
├── frontend/                 Next.js 15 application (TypeScript)
│   └── app/
│       ├── (auth)/           Login + Register pages
│       │   ├── login/
│       │   └── register/
│       └── (dashboard)/      Authenticated shell + feature pages
│
├── infra/
│   └── postgres/init.sql     Enables pgvector extension
│
├── alembic/                  Database migrations
│   └── versions/
│       └── 0001_multi_tenant_foundation.py
│
├── compose.yaml              Production Docker Compose
└── compose.dev.yaml          Local development overrides
```

---

## Multi-Tenant Architecture

Every resource in Engineering Memory belongs to exactly one **Organisation**.
The request lifecycle enforces tenant isolation at multiple layers:

```
JWT Token  →  X-Org-Slug Header  →  Membership check  →  Org-scoped repository query
```

### Models

| Model | Description |
|---|---|
| `Organization` | The tenant root. Has a globally unique `slug` (URL handle). |
| `User` | A platform user. Can belong to many organisations. |
| `Membership` | Links a User to an Organization with a role (`owner`/`admin`/`member`). |

### Roles

| Role | Permissions |
|---|---|
| `owner` | Full access; cannot be removed if last owner. |
| `admin` | Can add/remove members (not owners). |
| `member` | Read access; no admin actions. |

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js ≥ 20 (for frontend dev only)
- Python 3.12 (for backend dev only)

### 1. Configure environment

```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY
```

### 2. Start all services

```bash
docker compose up --build
```

This starts:
| Service | URL |
|---|---|
| API (FastAPI) | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Frontend (Next.js) | http://localhost:3000 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

### 3. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Verify

```bash
curl http://localhost:8000/health
# {"status": "ok"}

curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"mypassword","full_name":"Your Name"}'
```

---

## Development

### Backend

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Run tests

```bash
cd backend
pytest
```

### Lint & format

```bash
cd backend && ruff check . && ruff format .
cd frontend && npm run lint && npm run typecheck
```

---

## API Reference

Base URL: `http://localhost:8000/api/v1`

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | — | Register new account |
| `POST` | `/auth/login` | — | Login, receive JWT |
| `GET` | `/auth/me` | ✅ Bearer | Get current user |

### Organisations

All organisation routes require:
- `Authorization: Bearer <token>` header
- `X-Org-Slug: <slug>` header (except `POST /organizations`)

| Method | Path | Role | Description |
|---|---|---|---|
| `POST` | `/organizations` | authenticated | Create org (requester becomes owner) |
| `GET` | `/organizations/{slug}` | member | Get org details |
| `GET` | `/organizations/{slug}/members` | member | List members |
| `POST` | `/organizations/{slug}/members` | owner/admin | Add member |
| `DELETE` | `/organizations/{slug}/members/{user_id}` | owner/admin | Remove member |

---

## Roadmap

- [x] Multi-tenant foundation (Orgs, Users, Memberships, JWT auth)
- [ ] GitHub App integration (webhooks, PR sync)
- [ ] AI change understanding (OpenAI / Codex)
- [ ] Knowledge base auto-generation
- [ ] Natural language search (pgvector)
- [ ] Engineering timeline
- [ ] AI Engineering Advisor (chat interface)
- [ ] OAuth (GitHub, Google)
- [ ] Billing integration
