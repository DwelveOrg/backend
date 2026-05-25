# 00 - Current Repository Audit

## Status

This document summarizes the current FastAPI backend as observed from the repository.

The backend is not empty. It already contains a working FastAPI application structure with authentication, users, study groups, assignments, grades, dashboards, school-teacher relationships, Redis-backed token/session flows, and database models.

## Detected Stack

| Area | Current state |
|---|---|
| Framework | FastAPI |
| Server | Uvicorn |
| Database ORM | SQLAlchemy 2.x async |
| Default DB | SQLite with `aiosqlite` |
| Future DB target | PostgreSQL appears planned because `asyncpg` is commented in requirements |
| Migrations | Alembic dependency exists |
| Current table creation | `Base.metadata.create_all` runs during app startup |
| Auth | JWT access + refresh tokens |
| Password hashing | passlib bcrypt |
| Redis | pending registration, refresh tokens, token blacklist |
| Email | FastAPI-Mail |
| Rate limiting | SlowAPI |
| Tests | pytest, pytest-asyncio, httpx are installed |

## Entrypoint

Current app entrypoint:

```txt
main.py
```

The app currently creates:

```py
app = FastAPI(title="LMS Exam Prep API", lifespan=lifespan)
```

This title should eventually be renamed to Dwelve once the product naming is finalized.

## Current Startup Behavior

On startup, the app calls:

```py
await init_db()
```

`init_db()` currently imports `user`, `study_group`, `membership`, and `submission` directly, then runs:

```py
await conn.run_sync(Base.metadata.create_all)
```

This means tables are created automatically at runtime.

Important caveat: `assignment`, `grade`, and `school` are not imported directly inside `init_db()`. They are loaded elsewhere during normal app startup because `main.py` imports the routers first, but `init_db()` itself should import every model module explicitly if it remains responsible for `create_all`.

This is convenient for early development but risky for production. A production-ready backend should use Alembic migrations as the source of truth for schema changes.

## Current Routers

`main.py` includes these routers under `/api`:

```txt
/auth
/groups
/dashboard
/assignments
/school
/users
```

Exact behavior must be checked in each router before changing API contracts.

## Current Models

Detected model modules:

```txt
db/models/user.py
db/models/study_group.py
db/models/membership.py
db/models/assignment.py
db/models/grade.py
db/models/school.py
db/models/submission.py
```

### Main entities

Current entities include:

- `User`
- `StudyGroup`
- `GroupMembership`
- `Assignment`
- `AssignmentSubmission`
- `Grade`
- `SchoolTeacher`
- `TestSubmission`

## Current User Roles

Current roles:

```txt
student
teacher
school
```

The registration schema currently allows:

```txt
student
teacher
```

A separate `SchoolRegister` schema exists for school registration.

## Current Product Shape

The current backend looks like an LMS/exam-prep platform, not yet a complete multi-tenant Dwelve SaaS platform.

Current concepts:
- users
- groups
- group memberships
- assignments
- submissions
- grades
- school-teacher relations
- dashboard data

Missing or incomplete final Dwelve concepts may include:
- formal institution/workspace model
- institution membership with roles
- directors/admins
- classes as institution-scoped groups
- exams assigned to multiple classes
- analytics per institution
- subscription/payment model
- production migration workflow
- stronger tenant isolation

## Key Risks

### 1. Auto-create tables during startup

`Base.metadata.create_all` can hide migration problems. It should not be relied on for production.

### 2. Product naming mismatch

The FastAPI title says `LMS Exam Prep API`, while the product is now Dwelve.

### 3. Multi-tenancy is not complete yet

The current `school` role and `SchoolTeacher` link are not the same as a full workspace/institution model.

### 4. Role model may need redesign

Current roles are simple strings. Dwelve may require more granular roles:
- owner
- director
- admin
- teacher
- student

### 5. Redis dependency must be documented

Auth flows depend on Redis for pending registration, refresh tokens, and blacklist behavior.

### 6. SQLite is development-only

SQLite is fine for local development, but Dwelve SaaS should eventually use PostgreSQL.

## Recommended Next Steps

1. Confirm all routers work locally.
2. Add a real `.env.example`.
3. Add `python-dotenv` to `requirements.txt` or remove the `load_dotenv()` import from `app/core/email.py`.
4. Decide whether the current `school` user model becomes `Institution` or remains separate.
5. Introduce a true `Institution` / `Workspace` model if Dwelve is multi-tenant.
6. Move from `create_all` to Alembic-only migrations before production.
7. Add tests for auth, group creation, membership, assignment creation, and permission checks.
8. Rename API title and docs from LMS Exam Prep to Dwelve when ready.
