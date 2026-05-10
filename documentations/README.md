# Accurial Documentation

Documentation for the Accurial forecasting practice application.

## What is Accurial?

A self-hosted web application for personal forecasting practice, inspired by the principles in "Superforecasting: The Art and Science of Prediction" by Philip Tetlock and Dan Gardner.

Users create prediction questions, make probabilistic forecasts with confidence intervals, and track their calibration over time to improve their predictive abilities.

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy (async PostgreSQL) + Python 3.13
- **Frontend**: React 19 + TypeScript + Vite
- **Testing**: pytest with async support
- **Infra**: devbox, poetry, Docker Compose

## Quick Navigation

| Section | Purpose |
|---------|---------|
| [Getting Started](getting-started/index.md) | Environment setup and first run |
| [Architecture](architecture/overview.md) | System design, patterns, data flow |
| [Backend](backend/features.md) | Backend features and internals |
| [Frontend](frontend/setup.md) | Frontend setup, conventions, features |
| [Frontend Architecture](frontend/architecture/overview.md) | Frontend layered architecture |
| [Frontend Conventions](frontend/conventions/coding-style.md) | Frontend coding conventions |
| [Frontend Testing](frontend/testing.md) | Vitest + RTL + MSW setup |
| [Adding a Frontend Feature](frontend/adding-a-feature.md) | TDD-style step-by-step guide |
| [Development](development/tooling.md) | Tooling, conventions, adding features |
| [Deployment](deployment/docker.md) | Docker setup and production notes |
| [API](api/openapi.md) | API exploration via SwaggerUI |

## Agent References

Coding agents working on this codebase should refer to their specific agent files in `.opencode/agents/`:

- [Backend Agent `.opencode/agents/backend.md`](../.opencode/agents/backend.md) - Backend-specific conventions and patterns
- [Frontend Agent `.opencode/agents/frontend.md`](../.opencode/agents/frontend.md) - Frontend-specific conventions and patterns
- [Code Reviewer `.opencode/agents/code-reviewer.md`](../.opencode/agents/code-reviewer.md) - Code review subagent
- [Git Commit Pusher `.opencode/agents/git-commit-pusher.md`](../.opencode/agents/git-commit-pusher.md) - Git workflow conventions

When a doc file is relevant to an agent's task, its path should be referenced in the agent's prompt or context.
