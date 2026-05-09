# User

User management and authentication.

## Overview

Users are identified by email and authenticated with Argon2-hashed passwords. JWT tokens are used for session management via OAuth2 Password Bearer flow.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/user` | No | Register new user |
| GET | `/api/user/me` | Yes | Get current user |
| GET | `/api/user/{user_id}` | No | Get user by ID |
| GET | `/api/user/` | No | List users (filtered) |

## Key Behaviors

- Passwords are hashed with Argon2id before storage
- `UserRead` never exposes the hashed password
- Superuser can be auto-created on startup via `DEFAULT_EMAIL` / `DEFAULT_PASSWORD` env vars
- `is_active` flag controls account access

## Files

- `sources/backend/user/models.py`
- `sources/backend/user/schemas.py`
- `sources/backend/user/stores.py`
- `sources/backend/user/services.py`
- `sources/backend/user/apis.py`
