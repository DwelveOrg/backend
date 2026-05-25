# 05 - API and Routers

## Current API Prefix

All routers are currently included under:

```txt
/api
```

Example:

```txt
/api/auth/login
```

## Current Routers

Detected routers:

```txt
app/routers/auth.py
app/routers/dashboard.py
app/routers/groups.py
app/routers/assignments.py
app/routers/school.py
app/routers/users.py
```

## Auth Router

Current auth prefix:

```txt
/auth
```

Likely full paths:

```txt
POST /api/auth/register/start
POST /api/auth/register/verify
POST /api/auth/register/complete
POST /api/auth/login
POST /api/auth/refresh
POST /api/auth/logout
```

## API Design Rule

Do not change existing route paths unless necessary.

Frontend may already depend on these endpoints.

If route paths need to change, create a migration plan:
- keep old route temporarily
- add new route
- update frontend
- remove old route later

## Response Models

Schemas are currently in:

```txt
app/schemas.py
```

When adding a route:
- define a Pydantic request schema
- define a response schema where useful
- avoid returning raw SQLAlchemy models unless configured safely
- avoid leaking sensitive fields

## Current Domain Areas

### Users

User account identity and profile.

Current fields include:
- id
- full_name
- email
- password_hash
- paid_member
- created_at
- role

### Groups

Current `StudyGroup` appears to represent a learning group/class.

Current fields include:
- name
- subject
- tutor_name
- description
- group_type
- capacity
- is_private
- owner_id

### Memberships

Current `GroupMembership` links users to study groups.

### Assignments

Current `Assignment` belongs to a group and creator.

### Assignment Submissions

Current `AssignmentSubmission` links a student to an assignment.

### Grades

Current `Grade` links:
- assignment
- student
- grader
- score
- comment

### School

Current `SchoolTeacher` links one user with role `school` to a user with role `teacher`.

This is an early institution-teacher relationship, not a complete institution model.

## Future Dwelve API Direction

Long term, Dwelve may need endpoints like:

```txt
/api/institutions
/api/institutions/{institution_id}/members
/api/institutions/{institution_id}/classes
/api/institutions/{institution_id}/students
/api/institutions/{institution_id}/teachers
/api/institutions/{institution_id}/exams
/api/institutions/{institution_id}/results
/api/institutions/{institution_id}/analytics
```

Do not add these all at once. Add them when the product roadmap requires them.

## API Consistency Rules

Use:

- nouns for resources
- plural route names
- consistent status codes
- consistent error messages
- pagination for list endpoints
- auth dependencies for protected endpoints
- role dependencies for restricted endpoints

## Error Handling

Use `HTTPException` with clear status codes:

- `400` for invalid request state
- `401` for unauthenticated
- `403` for unauthorized
- `404` for missing resource
- `409` for conflicts such as duplicate email
- `422` for validation errors handled by FastAPI/Pydantic

## Pagination

Current schemas include pagination models.

Use pagination for:
- groups
- users
- assignments
- submissions
- results
- future institution lists
