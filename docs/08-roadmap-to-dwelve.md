# 08 - Roadmap from Current Backend to Dwelve

## Current State

The backend currently looks like an LMS/exam-prep system.

It already has useful foundations:

- auth
- users
- roles
- groups
- memberships
- assignments
- submissions
- grades
- school-teacher links
- dashboard concept
- Redis-backed token/session workflows

## Main Gap

Dwelve is supposed to be a multi-tenant SaaS for schools and learning centers.

The current backend does not yet appear to have a full institution/workspace model.

The current `school` role is not enough by itself because a user role and an institution are different concepts.

## Recommended Evolution

### Phase 1 - Stabilize Current Backend

Goals:
- make current app run reliably
- document routes
- add `.env.example`
- add basic tests
- confirm Redis/email setup
- confirm migrations status
- stop relying on `create_all` before production

### Phase 2 - Introduce Institution Model

Add formal institution/workspace concept.

Possible models:

```txt
Institution
InstitutionMember
InstitutionRole
```

Suggested roles:

```txt
owner
director
admin
teacher
student
```

### Phase 3 - Map Current Groups to Classes

Current `StudyGroup` can evolve into class/group functionality.

Possible options:

1. Keep `StudyGroup` and add `institution_id`.
2. Rename to `ClassGroup` later with migration.
3. Create a new `Class` model and migrate old groups later.

Do not rename immediately unless frontend and migrations are ready.

### Phase 4 - Exam/Assignment Model Decision

Current `Assignment` may become:
- homework assignment
- exam assignment
- generic task

Dwelve's product needs exams assigned to classes.

Possible future models:

```txt
Exam
ExamAssignment
Result
```

Current `Assignment`, `AssignmentSubmission`, and `Grade` may be reused or split.

### Phase 5 - Analytics

Add institution-scoped analytics.

Examples:
- class average score
- student performance
- exam completion rate
- teacher activity
- monthly institution stats

### Phase 6 - Subscriptions

Current `User.paid_member` is too simple for SaaS subscriptions.

Future subscription model should likely be institution-based:

```txt
SubscriptionPlan
InstitutionSubscription
Payment
```

Do not build payments until the core institution/class/exam flow is stable.

## Migration Strategy

Do not attempt to transform everything at once.

Recommended order:

1. Add tests for current auth and groups.
2. Add Institution model.
3. Connect school users to institutions.
4. Scope groups/classes to institutions.
5. Scope assignments/exams to institutions.
6. Scope analytics to institutions.
7. Replace simple `paid_member` with institution subscription.
8. Clean old naming after product structure is stable.

## Technical Debt to Watch

- all schemas are in one file
- `create_all` during startup
- simple role strings
- SQLite default
- possible mismatch between product name and API name
- unknown migration status
- Redis/email required but not fully documented here
- multi-tenancy not fully enforced yet
