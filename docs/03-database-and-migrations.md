# 03 - Database and Migrations

## Current Database Setup

The backend currently uses async SQLAlchemy.

The database setup is in:

```txt
db/db_ext.py
```

Current default database URL:

```txt
sqlite+aiosqlite:///./project.db
```

The app reads database config from:

```txt
DATABASE_URL
```

If `DATABASE_URL` is not set, it falls back to local SQLite.

## Current Session Dependency

Routes should use:

```py
db: AsyncSession = Depends(get_db)
```

from:

```txt
db.db_ext
```

## Current Base

The SQLAlchemy declarative base is in:

```txt
db/base.py
```

Current base:

```py
class Base(DeclarativeBase):
    pass
```

## Current Models

Current detected models:

```txt
User
StudyGroup
GroupMembership
Assignment
AssignmentSubmission
Grade
SchoolTeacher
TestSubmission
```

## Current Startup Table Creation

The backend currently calls `Base.metadata.create_all` during startup.

This is useful for early local development, but it is not a proper production migration strategy.

`db/db_ext.py` currently imports only some model modules before calling `create_all`. Normal app startup loads the remaining models through router imports, but a safer `init_db()` implementation would import all model modules explicitly:

```txt
db.models.user
db.models.study_group
db.models.membership
db.models.submission
db.models.assignment
db.models.grade
db.models.school
```

## Migration Policy

Alembic is listed as a dependency, so the backend should move toward Alembic as the source of truth for schema changes.

Recommended production rule:

```txt
Do not rely on create_all in production.
Use Alembic migrations.
```

## Local Development Rule

For now, while the project is still early, `create_all` may remain for convenience.

But any schema change should still be made migration-aware.

## Recommended Migration Workflow

When changing models:

1. Update the SQLAlchemy model.
2. Generate an Alembic migration.
3. Review the migration manually.
4. Apply the migration locally.
5. Test affected endpoints.
6. Commit model and migration together.

Typical commands, if Alembic is configured:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## SQLite vs PostgreSQL

SQLite is acceptable for local development.

For SaaS production, Dwelve should eventually use PostgreSQL because it handles:

- concurrent users better
- stronger constraints
- production deployment patterns
- indexing and analytics queries
- JSON fields if needed
- future scaling

The requirements already hint at PostgreSQL readiness because `asyncpg` is commented.

## Multi-Tenancy Database Requirement

Dwelve needs tenant isolation.

Future institution-scoped models should include an institution/workspace reference.

Example:

```txt
classes.institution_id
students.institution_id
teachers.institution_id
exams.institution_id
assignments.institution_id
results.institution_id
```

The current backend does not yet appear to have a formal `Institution` table. The current `school` role and `SchoolTeacher` relation are not enough for full SaaS multi-tenancy.

## Constraints

Use database constraints where appropriate:

- unique emails
- unique membership per user/group
- unique teacher/school relation
- unique grade per assignment/student
- minimum group capacity
- required foreign keys

Existing models already use some constraints. Preserve them.
