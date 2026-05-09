# Architecture Overview

High-level system design of Accurial.

## System Diagram

```
+-------------+      HTTP/REST      +------------------+
|  Frontend   |  <--------------->  |  FastAPI Backend |
|  (React 19  |      CORS enabled   |  (Python 3.13)   |
|   + Vite)   |                     |                  |
+-------------+                     +--------+---------+
                                             |
                                             | async SQLAlchemy
                                             |
                                     +-------v---------+
                                     |  PostgreSQL     |
                                     |  (asyncpg)      |
                                     +-----------------+
```

## Components

### Frontend

- **React 19** + **TypeScript** + **Vite**
- Currently in early development (template stage)
- API client in `sources/frontend/app/services/api.tsx`
- CSS styling with standard CSS files

### Backend

- **FastAPI** with async support
- **SQLAlchemy 2.0** with async PostgreSQL (`asyncpg`)
- **Pydantic** v2 for validation and serialization
- **Alembic** for database migrations (configured but codebase currently auto-creates tables)
- **PyJWT** + **OAuth2PasswordBearer** for authentication
- **Argon2** for password hashing
- **loguru** for logging

### Database

- **PostgreSQL** with async driver (`psycopg[binary,pool]` / `asyncpg`)
- Connection pooling configured (`pool_size=10`, `max_overflow=10`)
- Connection recycling every 30 minutes (`pool_recycle=1800`)

## Project Layout

```
Accurial/
├── sources/
│   ├── backend/              # FastAPI application
│   │   ├── auth/             # JWT authentication
│   │   ├── user/             # User management
│   │   ├── question/         # Prediction questions
│   │   ├── prediction/       # Forecasts & estimates
│   │   ├── resolution/       # Resolutions & scoring
│   │   ├── debug/            # Healthcheck endpoint
│   │   ├── utils/            # Shared utilities
│   │   ├── main.py           # Application entry point
│   │   ├── database.py       # SQLAlchemy engine & session
│   │   ├── settings.py       # Pydantic settings
│   │   └── exceptions.py     # Application exceptions
│   └── frontend/             # React application
│       ├── app/
│       │   ├── App.tsx
│       │   ├── main.tsx
│       │   ├── services/     # API client
│       │   └── components/   # UI components
│       └── ...config files
├── tests/
│   └── backend/              # pytest test suite
│       ├── conftest.py       # Fixtures & DB setup
│       ├── config.py
│       └── <feature>/        # Mirrors backend structure
├── deployments/
│   ├── docker-compose.dev.yml
│   ├── Dockerfile.dev
│   └── hooks/                # Git hooks
├── docs/                     # This documentation
├── documentations/           # Legacy docs (deprecated)
└── ...config files
```

## Request Lifecycle

1. **Client** sends HTTP request
2. **FastAPI Router** (`apis.py`) receives request
3. **Dependency Injection** (`dependencies.py`) validates JWT token
4. **External Schema** (`schemas.py`) validates request body
5. **API Layer** converts to **Internal Schema** (adds `user_id`, `context`)
6. **Service** (`services.py`) applies business logic
7. **Store** (`stores.py`) performs database CRUD
8. **Database** (`database.py`) executes SQL via SQLAlchemy
9. Response flows back through the same layers, converted to Read schema

See [Data Flow](data-flow.md) for detailed explanation.
