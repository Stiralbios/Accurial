# Frontend Tests

This directory mirrors `sources/frontend/app/features/` and contains the frontend test suite.

See `documentations/frontend/testing.md` for the full convention.

## Layout

```
tests/frontend/
├── setup/
│   ├── server.ts        # MSW server lifecycle
│   └── render.tsx       # custom render with providers
├── handlers/
│   ├── index.ts         # aggregates per-feature handlers
│   └── <feature>.ts     # one file per backend feature
├── factories/
│   └── <feature>.ts     # one file per feature
└── <feature>/           # test files mirroring sources/frontend/app/features/<feature>/
```

## Running

```
make test_frontend
# or
cd sources/frontend && npm run test
```
