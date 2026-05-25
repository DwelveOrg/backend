# 02 - Current Architecture

## Current High-Level Structure

The backend currently uses a simple FastAPI + SQLAlchemy architecture.

Detected important locations:

```txt
main.py
app/
  routers/
    auth.py
    dashboard.py
    groups.py
    assignments.py
    school.py
    users.py
  schemas.py
  core/
    security.py
    redis.py
    email.py
    logger.py
  dependencies/
    auth_deps.py
db/
  base.py
  db_ext.py
  models/
    user.py
    study_group.py
    membership.py
    assignment.py
    grade.py
    school.py
    submission.py
requirements.txt
```

Some files may exist beyond this list. Always inspect the actual repository.

## App Entrypoint

The app is created in `main.py`.

Current responsibilities of `main.py`:

- configure logging
- create FastAPI app
- run database initialization during lifespan
- configure rate limiting
- configure CORS
- include routers under `/api`
- define root endpoint
- run uvicorn in development

## Current Router Style

Routers are grouped by domain:

- `auth.py` handles registration, verification, login, refresh, logout
- `groups.py` handles study groups/classes and membership-related group behavior
- `dashboard.py` handles user dashboard data
- `assignments.py` handles assignments, submissions, and grades
- `school.py` handles school registration and school-teacher links
- `users.py` handles user profile/account behavior

Before editing a route, check:
- request schema
- response schema
- database queries
- permission dependencies
- frontend usage

## Current Data Layer

The backend uses:

```py
AsyncSession
async_sessionmaker
create_async_engine
```

The DB session dependency is:

```py
get_db()
```

from:

```txt
db/db_ext.py
```

All DB-using routes should depend on this function rather than creating sessions manually.

## Current Model Pattern

Models use SQLAlchemy 2.x style:

```py
Mapped[...]
mapped_column(...)
relationship(...)
```

Keep this style.

Do not mix in older SQLAlchemy model patterns unless there is a strong reason.

## Current Schema Pattern

Schemas are currently centralized in:

```txt
app/schemas.py
```

This is acceptable for a small project, but as the backend grows, schemas may be split by domain:

```txt
app/schemas/
  auth.py
  users.py
  groups.py
  assignments.py
  schools.py
```

Do not split schemas until the project becomes painful to maintain or the owner asks for cleanup.

## Suggested Target Architecture

Long term, Dwelve may benefit from:

```txt
app/
  main.py
  core/
    config.py
    security.py
    redis.py
    email.py
    logger.py
  db/
    session.py
    base.py
  models/
  schemas/
  routers/
  services/
  repositories/
  dependencies/
  tests/
```

However, the current project has `db/` at the repository root. Do not move it without a reason.

## Service Layer Recommendation

Current routers may contain business logic directly.

As the project grows, move complex logic into services:

```txt
app/services/
  auth_service.py
  group_service.py
  assignment_service.py
  school_service.py
  analytics_service.py
```

Routers should eventually focus on:
- HTTP input/output
- dependency injection
- calling service functions
- returning responses

Services should handle:
- business rules
- multi-step workflows
- permission-sensitive operations
