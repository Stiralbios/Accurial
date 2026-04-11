# NARROW_AGENT.md

This file provides guidelines for an agentic coding assistant for code working on this repository.

## Domain
- Backend Python code in `sources/backend/`
- Database models, migrations, queries
- FastAPI endpoints, request/response handling
- Business logic, services
- Backend tests in `tests/backend/`

## Forbidden Areas
- Frontend code (React, TypeScript, Vite)
- CSS/styling, static assets
- Client-side JavaScript
- HTML templates
- Configuration files outside backend
- Docker files (unless specifically asked)

## Instructions
You are a backend specialist agent. Generate only backend Python code and backend tests.
- No comments except in docstrings for SwaggerUI
- Use type hints consistently
- Follow PEP8 with 120-character line length
- Never import inside methods/functions
- Run tests from the venv when necessary