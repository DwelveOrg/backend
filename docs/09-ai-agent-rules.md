# 09 - AI Agent Rules

## Main Rule

Do not guess. Inspect the repository first.

## Before Editing

Always check:

- related router
- related schema
- related model
- auth dependency
- DB session usage
- Redis usage if auth/session-related
- email usage if registration-related
- tests if they exist

## Safe Change Pattern

Use this pattern:

1. Explain what exists.
2. Explain the problem.
3. Propose the smallest safe change.
4. Make the change.
5. Add/update tests if practical.
6. Update docs if behavior changes.

## Do Not Do These Without Approval

- migrate from FastAPI to NestJS
- replace SQLAlchemy
- replace JWT auth
- delete Redis logic
- remove email verification
- rename database tables
- rewrite all routers
- move the entire folder structure
- introduce payments
- introduce a completely new permission system

## Allowed Improvements

These are usually safe if done carefully:

- add `.env.example`
- add missing tests
- improve error messages
- add response models
- add pagination to list endpoints
- add indexes/constraints through migrations
- improve docs
- split large files gradually
- add service layer for complex logic
- improve security checks
- make role checks more explicit

## Code Style

Use:

- async SQLAlchemy consistently
- FastAPI dependency injection
- Pydantic v2 patterns
- clear type hints
- small functions
- explicit permission checks
- consistent HTTP status codes

## Database Change Rule

If a model changes, create or update an Alembic migration.

Do not rely only on `create_all`.

## Auth Change Rule

If auth changes, test:

- registration
- login
- refresh
- logout
- protected route access
- blacklisted token behavior
- role checks

## Multi-Tenancy Rule

Dwelve must prevent cross-institution data leaks.

Any future institution-scoped endpoint must filter by institution and verify membership/role.

## Documentation Rule

When major concepts change, update:

- `00-repo-audit.md`
- `02-current-architecture.md`
- `03-database-and-migrations.md`
- `04-auth-and-permissions.md`
- `08-roadmap-to-dwelve.md`

## Commit Rule

Prefer small commits with clear messages.

Good examples:

```txt
docs: add FastAPI backend audit
test: add auth login tests
fix: enforce group membership before assignment submission
feat: add institution model
refactor: move auth logic into service layer
```
