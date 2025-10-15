# Persephone API

Minimal viable FastAPI backend that orchestrates artifact uploads and mock GPU runs.

## Getting started

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Or use Docker Compose:

```bash
docker compose -f infra/compose.yaml up -d --build
```

Apply migrations:

```bash
alembic upgrade head
```

Check health:

```bash
curl http://localhost:8000/healthz
```

## First user

The initial Alembic migration seeds an admin user with credentials:

- Email: `admin@persephone.local`
- Password: `admin`

## Sample requests

```bash
# Login
curl -i -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@persephone.local","password":"admin"}'

# Who am I
curl -b 'psphn_session=...' http://localhost:8000/auth/me

# Upload artifact
curl -b 'psphn_session=...' -X POST http://localhost:8000/upload \
  -F 'file=@example.txt'

# List GPUs
curl http://localhost:8000/compute/gpus

# Prepare run
curl -b 'psphn_session=...' -X POST 'http://localhost:8000/prepare/start?runId=<id>&gpuId=a100'

# Deploy run
curl -b 'psphn_session=...' -X POST 'http://localhost:8000/deploy/start?runId=<id>'

# Check run status
curl -b 'psphn_session=...' http://localhost:8000/runs/<id>

# Cancel run
curl -b 'psphn_session=...' -X POST http://localhost:8000/runs/<id>/cancel

# Webhook
curl -X POST http://localhost:8000/monitor/webhook \
  -H 'X-Signature: <hmac>' \
  -H 'Content-Type: application/json' \
  -d '{"run_id":"<id>","phase":"running"}'
```

## Tests

```bash
pytest -q
```
