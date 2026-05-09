# Getting Started

Quick start guide for running the Accurial application locally.

## Prerequisites

- [devbox](https://www.jetify.com/devbox) installed
- Docker and Docker Compose installed
- Node.js (for frontend dev server)

## Environment Setup

The project uses `devbox` to manage the development environment.

```bash
# Enter the devbox shell (installs Python 3.13, poetry, and tools)
devbox shell

# Install Python dependencies
poetry install
```

## Environment Variables

Create a `.env` file at the project root with the following variables (see `sources/backend/settings.py`):

```bash
APP_ENVIRONMENT=DEV
LOG_LEVEL=DEBUG
JWT_SECRET_KEY=your-secret-key-here
JWT_ACCESS_TOKEN_EXPIRATION_MINUTES=60
RESET_PASSWORD_TOKEN_SECRET=your-reset-secret
VERIFICATION_TOKEN_SECRET=your-verification-secret
POSTGRES_HOST=project_base_postgres
POSTGRES_PORT=5432
POSTGRES_USER=dev
POSTGRES_PASSWORD=dev
POSTGRES_DB=dev
ALLOWED_CORS_ORIGINS=["http://localhost:5173"]

# Optional: auto-create superuser on startup
DEFAULT_EMAIL=admin@example.com
DEFAULT_PASSWORD=adminpassword
```

## Running the Application

### Full Stack (Docker)

```bash
# Start backend API + PostgreSQL + pgweb
make run_dev_env
```

This starts:
- API at `http://localhost:8800`
- SwaggerUI at `http://localhost:8800/docs`
- PostgreSQL at `localhost:5432`
- Test PostgreSQL at `localhost:5434`
- pgweb (DB GUI) at `http://localhost:8081`

### Frontend Only

```bash
# Run frontend dev server (Vite)
make run_dev_frontend
```

Frontend will be at `http://localhost:5173` with HMR enabled.

## Verify Everything Works

1. Open `http://localhost:8800/api/debug/healthcheck/status` - should return `{"status": "ok"}`
2. Open `http://localhost:8800/docs` - SwaggerUI with all endpoints
3. Frontend at `http://localhost:5173` - shows the Vite + React template

## Common Commands

| Command | Description |
|---------|-------------|
| `make run_dev_env` | Start Docker dev stack |
| `make run_dev_frontend` | Run frontend dev server |
| `make test` | Run backend tests |
| `make run_precommit` | Run all code quality tools |
| `make clean_dev_env` | Stop and remove Docker containers |
| `make build_docker` | Rebuild dev Docker image |
| `make go_in_docker` | Enter running dev container |
| `make clean` | Remove Python cache files |
