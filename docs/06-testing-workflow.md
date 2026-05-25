# 06 - Testing Workflow

## Current Testing Dependencies

The backend includes:

- pytest
- pytest-asyncio
- httpx

These are appropriate for testing async FastAPI endpoints.

## Current Tests

The repository currently has:

```txt
tests/conftest.py
tests/test_auth.py
tests/test_groups.py
tests/test_assignments.py
```

The test setup uses `sqlite+aiosqlite:///./test.db`, overrides `get_db`, mocks Redis with an in-memory store, and disables SlowAPI request-limit checks during tests.

## Testing Goals

The backend should have tests for:

- authentication
- authorization
- groups/classes
- memberships
- assignments
- submissions
- grades
- school-teacher links
- dashboard responses
- database constraints

## Recommended Test Structure

Suggested future structure:

```txt
tests/
  conftest.py
  test_auth.py
  test_users.py
  test_groups.py
  test_assignments.py
  test_school.py
  test_dashboard.py
```

## Testing Database

Use a separate test database.

Options:
- SQLite in-memory or temporary file for fast tests
- PostgreSQL test database for production-like behavior later

Do not run tests against the real development or production database.

## Testing Redis

Auth currently depends on Redis for:
- pending registration
- refresh tokens
- token blacklist

For tests, choose one:

1. Use a test Redis instance.
2. Mock Redis functions.
3. Use fakeredis if added to dependencies.

Do not let tests depend on production Redis.

## Important Auth Tests

Test:

- registration start sends/stores verification
- duplicate email is rejected
- invalid verification code is rejected
- registration complete requires verification
- weak password is rejected
- login works with correct credentials
- login fails with wrong password
- refresh works with valid refresh token
- refresh fails with missing/revoked refresh token
- logout blacklists access token

## Important Permission Tests

Test:

- student cannot create restricted teacher/school resources
- teacher can create groups if allowed
- school can link teacher if allowed
- user cannot access another user's private data
- student cannot submit to assignment outside their group
- teacher cannot grade outside permitted group

## API Testing Pattern

Use `httpx.AsyncClient` with the FastAPI app.

Example style:

```py
@pytest.mark.asyncio
async def test_login_success(client):
    response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 200
```

Adjust fixtures to match the actual project.

## Regression Rule

When fixing a bug, add a test that would have failed before the fix.

## Refactor Rule

Before major refactors:
1. Add tests for current behavior.
2. Refactor.
3. Confirm tests still pass.
