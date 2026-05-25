# 07 - Environment and Deployment

## Current Environment Variables

Detected important environment variables:

```txt
DATABASE_URL
DEBUG
SECRET_KEY
TESTING
SCHOOL_SECRET_KEY
REDIS_URL
MAIL_USERNAME
MAIL_PASSWORD
MAIL_FROM
MAIL_SERVER
```

Redis and email settings are currently read from:

```txt
app/core/redis.py
app/core/email.py
```

## Required Variable

`SECRET_KEY` is required. The app should not start without it.

## Database Variable

`DATABASE_URL` defaults to:

```txt
sqlite+aiosqlite:///./project.db
```

For production, use PostgreSQL:

```txt
postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DB_NAME
```

This requires enabling `asyncpg` in dependencies.

## Debug

`DEBUG` currently controls SQLAlchemy echo and uvicorn reload behavior.

Production should use:

```txt
DEBUG=false
```

## CORS

Current CORS allows:

```txt
http://localhost:3000
```

For production, add the real frontend domain.

Do not use unrestricted `*` origins in production with credentials enabled.

## Redis

Redis is required for current auth behavior.

Production needs:

```txt
REDIS_URL
```

or equivalent config depending on how `app/core/redis.py` is implemented.

## Email

Registration verification depends on email sending.

Production needs these variables for the current `ConnectionConfig`:

```txt
MAIL_USERNAME
MAIL_PASSWORD
MAIL_FROM
MAIL_SERVER
```

`MAIL_PORT`, `MAIL_STARTTLS`, and `MAIL_SSL_TLS` are currently hard-coded in `app/core/email.py`.

`app/core/email.py` imports `dotenv.load_dotenv`, but `python-dotenv` is not currently listed in `requirements.txt`. A fresh install may fail until that dependency is added or the import is removed.

## Deployment Checklist

Before deployment:

- set `SECRET_KEY`
- set production `DATABASE_URL`
- set Redis config
- set email config
- set `DEBUG=false`
- configure CORS
- run migrations
- do not rely on `create_all`
- run tests
- check `/docs`
- verify registration email flow
- verify login/refresh/logout
- verify protected routes
- verify logs do not expose secrets

## Production Database Rule

Production should use Alembic migrations.

Do not use SQLite for real users.

## Recommended Hosting Options

Good beginner-friendly options:

- Render
- Railway
- Fly.io
- DigitalOcean App Platform

For database:
- Neon PostgreSQL
- Supabase PostgreSQL
- Railway PostgreSQL
- Render PostgreSQL

For Redis:
- Upstash Redis
- Railway Redis
- Render Redis if available

## Docker

```txt
Dockerfile
docker-compose.yml
```

These files already exist. Current local compose includes:

- backend
- Redis
- nginx

It still uses SQLite through a mounted `project.db` file by default. Add PostgreSQL to compose when the backend is ready to move away from SQLite.
