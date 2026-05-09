# API Reference

The FastAPI backend serves an interactive SwaggerUI documentation page.

## SwaggerUI

**URL**: `http://localhost:8800/docs`

Available when the application is running. Contains:
- All endpoint definitions
- Request/response schemas
- Authentication flow (Authorize button for JWT)
- Try-it-now functionality

## Authentication

SwaggerUI uses OAuth2 Password Bearer flow:

1. Click **Authorize** button
2. Enter username (email) and password
3. Click **Authorize**
4. All protected endpoints will include the `Authorization: Bearer <token>` header

## Base URL

- Development: `http://localhost:8800`

## Endpoint Prefixes

| Prefix | Feature | Auth Required |
|--------|---------|--------------|
| `/api/debug/healthcheck` | Health check | No |
| `/api/auth` | Authentication | Partial |
| `/api/user` | User management | Partial |
| `/api/question` | Questions | Yes |
| `/api/prediction` | Predictions | Yes |
| `/api/resolution` | Resolutions | Yes |

## OpenAPI Schema

The OpenAPI JSON schema is available at:

```
http://localhost:8800/openapi.json
```

This can be used to generate client SDKs or import into API tools like Postman.

## Health Check

```bash
curl http://localhost:8800/api/debug/healthcheck/status
```

Response:
```json
{
  "status": "ok",
  "stack": {
    "python": "3.13.x"
  }
}
```
