# CFM Fittings Pro – Deployment Guide

## Quick Start (Docker Compose)

```bash
# 1. Clone and enter the repository
git clone <repo-url>
cd WIZARD-FITTINGS-V1

# 2. Configure environment
cp .env.example .env
# Edit .env with your secure values

# 3. Start all containers
docker compose up --build -d

# 4. Run database migrations (first time)
docker exec cfm_backend alembic upgrade head

# 5. Access the platform
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Services

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| Frontend | cfm_frontend | 5173 | React UI |
| Backend | cfm_backend | 8000 | FastAPI REST API |
| Database | cfm_postgres | 5432 | PostgreSQL 16 |

## First-Time Setup

After running migrations, register your first tenant via:
- UI: http://localhost:5173/register
- API: POST http://localhost:8000/api/v1/auth/register

## Running Tests Inside Containers

```bash
# Backend tests
docker exec cfm_backend pytest -v

# Frontend tests
docker exec cfm_frontend npm test
```

## Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Container status
docker compose ps
docker compose logs cfm_backend
```

## Volumes

- `cfm_postgres_data` – PostgreSQL data persistence
- `cfm_storage` – File exports (PDF, DXF, Excel, CSV, JSON)

## Production Deployment

1. Set `APP_ENV=production` and `DEBUG=false` in `.env`
2. Change all secrets (`SECRET_KEY`, `POSTGRES_PASSWORD`)
3. Use `target: production` in docker-compose.yml
4. Set up a reverse proxy (nginx/traefik) in front of both services
5. Configure SSL/TLS certificates
