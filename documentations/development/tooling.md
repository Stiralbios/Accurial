# Tooling

Development tools and commands for Accurial.

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make run_dev_env` | Start Docker dev stack (API + Postgres + pgweb) |
| `make clean_dev_env` | Stop and remove Docker containers |
| `make build_docker` | Rebuild dev Docker image |
| `make go_in_docker` | Enter running dev container |
| `make test` | Run pytest backend tests |
| `make run_precommit` | Run all pre-commit hooks on all files |
| `make install_hooks` | Install git hooks |
| `make run_dev_frontend` | Start frontend Vite dev server |
| `make clean` | Remove Python cache files |
| `make stow` | Apply devconfigs via stow |

## Code Quality Tools

Configured in `pyproject.toml`:

### Ruff
- Line length: 120 characters
- Target Python: 3.13
- Docstring code formatting enabled
- Import sorting (`extend-select = ["I"]`)

Run: `ruff check . && ruff format .`

### flake8
- Config in `.flake8`

Run: `flake8 sources/ tests/`

### mypy
- Config in `mypy.ini`

Run: `mypy sources/`

### bandit
- Security linting
- Config in `.bandit`

Run: `bandit -r sources/`

## Pre-commit Hooks

Configured in `.pre-commit-config.yaml`. Runs automatically on commit.

## Testing

```bash
# Run all tests
make test

# With coverage
poetry run pytest --cov

# Verbose
poetry run pytest -v
```

## devbox

Provides the development environment:

```bash
# Enter shell
devbox shell

# Run a command
devbox run <command>
```
