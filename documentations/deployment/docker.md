# Docker Deployment

Docker-based development and deployment setup.

## Development Stack

Services are defined in `deployments/docker-compose.dev.yml`.

### Services

| Service | Container Name | Port | Image |
|---------|---------------|------|-------|
| API | `project_base_dev` | `8800` | Built from `Dockerfile.dev` |
| PostgreSQL | `project_base_postgres` | `5432` | Official Postgres |
| Test PostgreSQL | `project_base_postgres_test` | `5434` | Official Postgres |
| pgweb | `project_base_pgweb` | `8081` | Official pgweb |

### Dockerfile

`deployments/Dockerfile.dev` - Development image based on Python 3.13 with:
- Poetry installed
- Devbox shell available
- Project copied to `/home/project_base`
- Virtual environment at `.venv`

## Commands

```bash
# Start all services
make run_dev_env

# Stop and remove
make clean_dev_env

# Rebuild image (after Dockerfile or dependency changes)
make build_docker

# Enter running container
make go_in_docker
```

## Environment Configuration

The `.env` file at project root is loaded by Docker Compose. Key variables:

```bash
POSTGRES_HOST=project_base_postgres
POSTGRES_PORT=5432
POSTGRES_USER=dev
POSTGRES_PASSWORD=dev
POSTGRES_DB=dev
ALLOWED_CORS_ORIGINS=["http://localhost:5173"]
```

## Clean Development Environment

```bash
make clean_dev_env
```

Stops and removes all containers safely (returns 0 if containers don't exist).
