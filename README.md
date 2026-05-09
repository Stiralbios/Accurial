# Accurial

A self-hosted web application for personal forecasting practice, inspired by the principles in "Superforecasting: The Art and Science of Prediction" by Philip Tetlock and Dan Gardner.

## Documentation

Project documentation is in the [`docs/`](docs/README.md) directory.

## Setup

This project uses devbox for environment setup. See [`docs/getting-started/`](docs/getting-started/index.md) for detailed instructions.

### Quick Start

```bash
devbox shell
poetry install
make run_dev_env      # Start backend + database
make run_dev_frontend # Start frontend dev server
```

- API: http://localhost:8800
- SwaggerUI: http://localhost:8800/docs
- Frontend: http://localhost:5173
