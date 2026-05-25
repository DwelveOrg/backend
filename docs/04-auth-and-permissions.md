# 04 - Auth and Permissions

## Current Auth System

The backend currently uses:

- JWT access tokens
- JWT refresh tokens
- passlib bcrypt password hashing
- Redis-backed pending registration
- Redis-backed refresh token storage
- Redis-backed token blacklist
- FastAPI `HTTPBearer`

## Secret Key

The backend requires:

```txt
SECRET_KEY
```

If this is missing, `app/core/security.py` raises a runtime error.

This is good for security because the app should not silently run with an insecure default secret.

## Current Registration Flow

Current registration appears to be multi-step:

1. `/auth/register/start`
2. `/auth/register/verify`
3. `/auth/register/complete`

The start step:
- checks duplicate email
- generates a 6-digit verification code
- stores pending registration in Redis
- sends verification email

The verify step:
- checks the code
- marks the pending registration as verified

The complete step:
- checks password confirmation
- checks terms acceptance
- checks email verification
- creates the user
- hashes the password
- deletes pending registration data

## Current Login Flow

Login:
- checks email/password
- creates access token
- creates refresh token
- stores refresh token in Redis
- returns tokens

## Current Logout Flow

Logout:
- requires bearer access token
- blacklists the access token in Redis
- deletes the user's refresh token
- returns success

## Current Roles

Detected roles:

```txt
student
teacher
school
```

The `User` model exposes helper properties:

```txt
is_student
is_teacher
is_school
can_create_groups
```

Current role permission helper:

```py
role_required(*allowed_roles)
```

Current premium helper:

```py
premium_required
```

## Dwelve Role Concern

The current role system is probably too simple for final Dwelve.

Future Dwelve roles may need:

- platform owner
- institution owner
- director
- admin
- teacher
- student
- parent, optional later

Do not replace roles immediately. First check how current routers depend on `student`, `teacher`, and `school`.

## Permission Rules

Every protected endpoint must check:

1. Is the user authenticated?
2. Is the user allowed to perform this action?
3. Is the target resource owned by or connected to the user's institution/school/group?
4. Is premium/subscription access required?

## Tenant Isolation Rule

Do not rely on frontend filtering.

Backend routes must enforce data access.

Examples:
- a teacher should not grade students outside their group/school
- a student should not submit to assignments outside their group
- a school should not manage teachers it has not linked to
- future institutions must not access other institutions' data

## Security Rules

Never expose:

- `password_hash`
- raw JWT secrets
- refresh tokens except during login/refresh responses
- Redis keys
- environment variables
- email verification codes in responses

## Auth Testing Priorities

Add tests for:

- duplicate email registration
- invalid verification code
- complete registration without verification
- login with invalid password
- login success
- refresh token success
- invalid refresh token
- logout blacklists token
- protected route rejects missing token
- protected route rejects blacklisted token
- role-based restrictions
