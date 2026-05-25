# AGENTS.md - Dwelve FastAPI Backend Agent Guide

## Purpose

This file is the main instruction file for AI coding agents working on the Dwelve FastAPI backend.

This repository is an existing FastAPI backend. It has already been worked on and should not be treated as an empty project or a starter template.

The current backend appears to be an early LMS / exam-prep backend that must be carefully evolved into Dwelve.

## Current Backend Summary

Detected current stack:

- Framework: FastAPI
- Runtime/server: Uvicorn through `fastapi[standard]`
- Database layer: async SQLAlchemy 2.x
- Default database: SQLite through `sqlite+aiosqlite:///./project.db`
- PostgreSQL readiness: `asyncpg` is mentioned but currently commented out in `requirements.txt`
- Migrations: Alembic is installed, but the app currently also creates tables on startup using `Base.metadata.create_all`
- Auth: JWT with `python-jose`
- Password hashing: passlib with bcrypt
- Rate limiting: SlowAPI
- Email: FastAPI-Mail
- Redis: used for pending registrations, refresh tokens, and token blacklist
- Testing dependencies: pytest, pytest-asyncio, httpx

Detected current app entrypoint:

- `main.py`

Detected current routers imported by `main.py`:

- `app.routers.auth`
- `app.routers.dashboard`
- `app.routers.groups`
- `app.routers.assignments`
- `app.routers.school`
- `app.routers.users`

Detected current model modules:

- `db.models.user`
- `db.models.study_group`
- `db.models.membership`
- `db.models.assignment`
- `db.models.grade`
- `db.models.school`
- `db.models.submission`

Known setup caveat:

- `app/core/email.py` imports `dotenv.load_dotenv`, but `python-dotenv` is not currently listed in `requirements.txt`. Add it before relying on `.env` loading in a fresh environment, or remove the import if configuration will be injected another way.

## Product Context

Dwelve is a multi-tenant SaaS platform for schools and learning centers.

The final Dwelve product should help institutions manage:

- institutions / schools / workspaces
- directors and admins
- teachers
- classes / groups
- students
- assignments or exams
- student submissions
- grading / results
- analytics and dashboards
- subscription-based access

The current backend does not yet fully match the final Dwelve product model. It currently looks closer to an LMS/exam-prep backend with users, study groups, assignments, submissions, grades, and school-teacher relationships.

## Primary Rule

Before coding, inspect the existing backend.

Do not assume:
- the current schema is final
- the current role system is final
- the current groups model equals final Dwelve classes
- the current `school` role equals a complete institution/workspace model
- Alembic migrations are actively used correctly
- frontend expectations are fully documented
- the backend is production-ready

## Development Strategy

The safest strategy is:

1. Audit the existing code.
2. Document current behavior.
3. Identify gaps between the current LMS-style backend and the final Dwelve SaaS model.
4. Stabilize auth, database, migrations, and tests.
5. Add missing Dwelve concepts gradually.
6. Avoid large rewrites unless the project owner explicitly approves.

## Do Not Randomly Rewrite

Avoid:
- deleting existing routers without tracing frontend usage
- replacing SQLAlchemy with another ORM
- replacing FastAPI with another framework
- creating duplicate `User`, `School`, `Group`, or `Assignment` models
- renaming tables without migrations
- moving many files in one commit without tests
- changing JWT behavior without checking auth routes and frontend token handling

Prefer:
- small changes
- clear commits
- tests around existing behavior
- migration-safe schema evolution
- documentation updates after architectural decisions

## Recommended Agent Workflow

For every feature or fix:

1. Read the related router.
2. Read related schemas.
3. Read related models.
4. Check dependencies and permissions.
5. Check whether Redis, email, or background behavior is involved.
6. Check if DB schema changes are needed.
7. Add/update Alembic migration if schema changes are made.
8. Add/update tests.
9. Update docs if behavior changes.

## Important Docs

Read these files before editing:

- `docs/backend-fastapi/00-repo-audit.md`
- `docs/backend-fastapi/01-project-context.md`
- `docs/backend-fastapi/02-current-architecture.md`
- `docs/backend-fastapi/03-database-and-migrations.md`
- `docs/backend-fastapi/04-auth-and-permissions.md`
- `docs/backend-fastapi/05-api-and-routers.md`
- `docs/backend-fastapi/06-testing-workflow.md`
- `docs/backend-fastapi/07-env-and-deployment.md`
- `docs/backend-fastapi/08-roadmap-to-dwelve.md`
- `docs/backend-fastapi/09-ai-agent-rules.md`
