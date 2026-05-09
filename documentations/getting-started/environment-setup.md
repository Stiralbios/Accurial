# Environment Setup

Detailed environment setup for Accurial.

## devbox

This project uses [devbox](https://www.jetify.com/devbox) to provide a reproducible development environment.

```bash
# Enter the shell (packages defined in devbox.json)
devbox shell

# The shell provides:
# - Python 3.13
# - poetry
# - pre-commit
# - ruff
# - and other dev tools
```

## Poetry

Python dependencies are managed with poetry:

```bash
# Install all dependencies (including dev)
devbox run poetry install

# Add a dependency
devbox run poetry add <package>

# Add a dev dependency
devbox run poetry add --group dev <package>

# Run commands inside the venv
poetry run pytest
poetry run python sources/backend/main.py
```

## Pre-commit Hooks

Install git hooks for automatic code quality checks:

```bash
# Install hooks
make install_hooks

# Run manually on all files
make run_precommit
```

Or using devbox directly:

```bash
devbox run pre-commit run --all-files
```

## Environment Variables Reference

Defined in `sources/backend/settings.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENVIRONMENT` | `PROD` | `PROD`, `DEV`, or `TEST` |
| `LOG_LEVEL` | `DEBUG` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `JWT_SECRET_KEY` | required | Secret for JWT tokens |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_ACCESS_TOKEN_EXPIRATION_MINUTES` | `60` | Token expiration time |
| `RESET_PASSWORD_TOKEN_SECRET` | required | Token for password reset |
| `VERIFICATION_TOKEN_SECRET` | required | Token for email verification |
| `POSTGRES_HOST` | `project_base_postgres` | PostgreSQL host |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |
| `POSTGRES_USER` | `dev` | Database user |
| `POSTGRES_PASSWORD` | `dev` | Database password |
| `POSTGRES_DB` | `dev` | Database name |
| `ALLOWED_CORS_ORIGINS` | required | List of allowed CORS origins |
| `DEFAULT_EMAIL` | `None` | Auto-create superuser email |
| `DEFAULT_PASSWORD` | `None` | Auto-create superuser password |

## VS Code

VS Code settings are in `.vscode/`. The workspace file `Accurial.code-workspace` configures the project layout.

For devconfigs management via stow:

```bash
make stow
```

## Running the Application

### Docker Development Stack

```bash
# Start backend API + PostgreSQL + pgweb
make run_dev_env
```

Services:
- API at `http://localhost:8800`
- SwaggerUI at `http://localhost:8800/docs`
- PostgreSQL at `localhost:5432`
- Test PostgreSQL at `localhost:5434`
- pgweb (DB GUI) at `http://localhost:8081`

### Frontend Development Server

```bash
# Run frontend dev server (Vite)
make run_dev_frontend
```

Frontend at `http://localhost:5173` with HMR enabled.

### Verify Setup

1. Health Check: `curl http://localhost:8800/api/debug/healthcheck/status`
2. SwaggerUI: `http://localhost:8800/docs`
3. Database UI: `http://localhost:8081`

### Running Tests

Tests run against the test PostgreSQL instance at `localhost:5434`.

```bash
make test
# Or with poetry directly
poetry run pytest
```

### Typical Development Workflow

```bash
# 1. Enter devbox shell
devbox shell

# 2. Start backend and database
make run_dev_env

# 3. In another terminal, start frontend
make run_dev_frontend

# 4. Develop with both running

# 5. Run tests before committing
make test

# 6. Run code quality checks
make run_precommit

# 7. Stop everything
make clean_dev_env
```
