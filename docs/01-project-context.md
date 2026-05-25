# 01 - Dwelve Project Context

## What Dwelve Is

Dwelve is a SaaS platform for schools and learning centers.

Its purpose is to centralize academic operations such as:

- managing institutions
- managing directors/admins
- managing teachers
- managing students
- creating classes/groups
- assigning exams or assignments
- recording scores/results
- showing analytics and dashboards
- managing subscription access

## Current Backend Reality

The current FastAPI backend is not yet a full Dwelve SaaS backend.

It currently looks like an LMS / exam-prep backend with:

- users
- roles: student, teacher, school
- study groups
- memberships
- assignments
- assignment submissions
- grades
- test submissions
- dashboard routes
- school-teacher connections

This is a useful foundation, but the final Dwelve model needs stronger multi-tenancy and institution-level ownership.

## Product Evolution Direction

The current backend should evolve from:

```txt
LMS/exam-prep backend
```

toward:

```txt
multi-tenant school and learning-center management SaaS
```

Do not assume the current code is wrong. Many pieces may be reusable.

Possible mapping:

| Current concept | Possible Dwelve meaning |
|---|---|
| `User` | account identity |
| `school` role | early version of institution owner |
| `StudyGroup` | early class/group concept |
| `GroupMembership` | early enrollment/membership concept |
| `Assignment` | may become assignment/exam/task |
| `Grade` | result/score |
| `SchoolTeacher` | early institution-teacher relation |

## Final Dwelve Concepts

Dwelve will likely need these stable domain concepts:

- `Institution`
- `InstitutionMember`
- `Role`
- `User`
- `TeacherProfile`
- `StudentProfile`
- `Class`
- `ClassEnrollment`
- `Subject`
- `Exam`
- `ExamAssignment`
- `Result`
- `AnalyticsSnapshot`
- `SubscriptionPlan`
- `Subscription`

Do not create all of these immediately. Add them only when the product needs them and after checking the current schema.

## Product Rules

Dwelve must support multiple institutions.

That means:

- school A must not see school B data
- teacher A must not access another institution unless invited
- students must only see their own institution/class data
- dashboards must be scoped
- analytics must be tenant-safe

## Current Naming Issue

The backend currently uses names like:

- `LMS Exam Prep API`
- `StudyGroup`
- `TestSubmission`

These names may remain during early development, but long term they should be reviewed and aligned with Dwelve terminology.

Avoid renaming everything immediately. Rename only with migrations, tests, and frontend coordination.
