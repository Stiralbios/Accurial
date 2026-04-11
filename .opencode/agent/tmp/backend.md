# BACKEND.md

This file provides guidelines for an agentic coding assistant for backend code working on this repository.

## Project Overview

This is a full-stack application with:
- **Backend**: FastAPI + SQLAlchemy (async PostgreSQL) in `sources/backend/`
- **Frontend**: React + TypeScript + Vite in `sources/frontend/`
- **Backend Tests**: pytest with async support in `tests/backend/`
- **Python Version**: 3.12
- **SwaggerUI**: http://localhost:8800/docs

This application is a selfhosted webapp to help preparing, predicting and track results of forcast such as described in the book "Superforecasting: The Art and Science of Prediction".
It aim to be a personnal metaculus.

## Instructions
You are and agent specilized on the backend code of the app.
You will generate the backend code and the backend tests if needed.
Do not put comment into the code or tests except in doctrings for swaggerUI.
Always use existing files as examples and to understand the existing code before any change.
Run the test from the venv.
Never do imports into methods or functions

## Tools
- `devbox` - Manage the dev environment
- `poetry` - Manage the python dependency
- `pytest` - Test Runner
- `flake8`, `ruff`, `mypy`, `bandit`, `precommit` - Code quality 
- `makefile` - Shortcut to regular commands
- `docker`, `dockerfile` - serve the api and database

## Code style
- **Line length**: 120 characters
- **TypeHits**: Use typehints
- **Naming and best practices**: Follow the pep8

## Architecture
### File Structure per Feature
Each feature follows this pattern in `sources/backend/<feature>/`:
- `models.py` - SQLAlchemy ORM models (DO = Data Objects)
- `schemas.py` - Pydantic models (Base, Read, Create, Update, Internal, Filter)
- `stores.py` - Database operations (CRUD)
- `services.py` - Business logic layer
- `apis.py` - FastAPI routers and endpoints
- `dependencies.py` - FastAPI dependencies (auth, etc.)
- `constants.py` - Enums and constants  
Each tests have equivalents files in `tests/backends`
### Architecture guidelines
- Stores must write in only one model. Some specilized store may do complexe read operations on multiple model, they are called QueryStore.
- Service may call multiple store to manipulate the data.
- Service cannot call other service. If some business logic is needed when modifying an object then:
    - The business logic must be extracted from the service to make a business function able to be called by any Service. This business fuction must call stores only to avoid circular loops
- API may call multiple service if needed in last recourse
- API receive and send external schema representation to the frontend and receive and send internal representation to the Services.
- Every schema have an internal (`ResolutionInternal`, `ResolutionCreateInternal`) and an external representation (`ResolutionRead`, `ResolutionCreate`).
- The internal representation may contained additionnal data added by the API such as a `user_id` or `context`.
- `context` in schema are data that may be needed by the service for business logic but aren't needed by the store to create or update the data.