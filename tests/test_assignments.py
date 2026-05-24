import pytest
import json
from unittest.mock import patch


async def register_and_login(client, email, role, store):
    with patch("app.routers.auth.send_verification_email"):
        await client.post("/api/auth/register/start", json={
            "full_name": "Test User",
            "email": email,
            "role": role
        })
        raw = store.get(f"pending:{email}")
        data = json.loads(raw)
        code = data["code"]

        await client.post("/api/auth/register/verify", json={
            "email": email,
            "code": code
        })
        await client.post("/api/auth/register/complete", json={
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!",
            "accept_terms": True
        })

    response = await client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!",
    })
    return response.json()["access_token"]


async def create_group(client, token):
    response = await client.post("/api/groups/", json={
        "name": "Math Group",
        "subject": "Math",
        "tutor_name": "Mr. Smith",
        "description": "Advanced math group",
        "capacity": 10,
        "is_private": False,
        "group_type": "student"
    }, headers={"Authorization": f"Bearer {token}"})
    return response.json()["id"]


@pytest.mark.asyncio
async def test_teacher_can_create_assignment(client, redis_store):
    teacher_token = await register_and_login(client, "teacher@example.com", "teacher", redis_store)
    group_id = await create_group(client, teacher_token)

    response = await client.post(f"/api/assignments/{group_id}", json={
        "title": "Math Homework",
        "description": "Solve problems 1-10",
        "due_date": None
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_student_cannot_create_assignment(client, redis_store):
    teacher_token = await register_and_login(client, "teacher@example.com", "teacher", redis_store)
    student_token = await register_and_login(client, "student@example.com", "student", redis_store)
    group_id = await create_group(client, teacher_token)

    response = await client.post(f"/api/assignments/{group_id}", json={
        "title": "Math Homework",
        "description": "Solve problems 1-10",
        "due_date": None
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_teacher_can_grade_student(client, redis_store):
    teacher_token = await register_and_login(client, "teacher@example.com", "teacher", redis_store)
    student_token = await register_and_login(client, "student@example.com", "student", redis_store)
    group_id = await create_group(client, teacher_token)

    # Студент вступает в группу
    await client.post(f"/api/groups/{group_id}/join",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    # Учитель создаёт задание
    assignment_response = await client.post(f"/api/assignments/{group_id}", json={
        "title": "Math Homework",
        "description": "Solve problems 1-10",
        "due_date": None
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    assignment_id = assignment_response.json()["id"]

    # Получаем id студента
    dashboard = await client.get("/api/dashboard/",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    student_id = dashboard.json()["user"]["id"]

    # Учитель ставит оценку
    response = await client.post(f"/api/assignments/{assignment_id}/grade", json={
        "student_id": student_id,
        "score": 95.0,
        "comment": "Excellent work!"
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_cannot_grade_twice(client, redis_store):
    teacher_token = await register_and_login(client, "teacher@example.com", "teacher", redis_store)
    student_token = await register_and_login(client, "student@example.com", "student", redis_store)
    group_id = await create_group(client, teacher_token)

    await client.post(f"/api/groups/{group_id}/join",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assignment_response = await client.post(f"/api/assignments/{group_id}", json={
        "title": "Math Homework",
        "description": "Solve problems 1-10",
        "due_date": None
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    assignment_id = assignment_response.json()["id"]

    dashboard = await client.get("/api/dashboard/",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    student_id = dashboard.json()["user"]["id"]

    # Первая оценка
    await client.post(f"/api/assignments/{assignment_id}/grade", json={
        "student_id": student_id,
        "score": 95.0,
        "comment": "Excellent!"
    }, headers={"Authorization": f"Bearer {teacher_token}"})

    # Вторая оценка — должен быть 409
    response = await client.post(f"/api/assignments/{assignment_id}/grade", json={
        "student_id": student_id,
        "score": 80.0,
        "comment": "Try again"
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    assert response.status_code == 409

async def register_and_login(client, email, role, store):
    with patch("app.routers.auth.send_verification_email"):
        await client.post("/api/auth/register/start", json={
            "full_name": "Test User",
            "email": email,
            "role": role
        })
        raw = store.get(f"pending:{email}")
        data = json.loads(raw)
        code = data["code"]

        await client.post("/api/auth/register/verify", json={
            "email": email,
            "code": code
        })
        await client.post("/api/auth/register/complete", json={
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!",
            "accept_terms": True
        })

    response = await client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_student_can_submit_assignment(client, redis_store):
    teacher_token = await register_and_login(client, "teacher@example.com", "teacher", redis_store)
    student_token = await register_and_login(client, "student@example.com", "student", redis_store)

    # Создаём группу
    group_response = await client.post("/api/groups/", json={
        "name": "Math Group",
        "subject": "Math",
        "tutor_name": "Mr. Smith",
        "description": "Advanced math group",
        "capacity": 10,
        "is_private": False,
        "group_type": "student"
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    group_id = group_response.json()["id"]

    # Студент вступает
    await client.post(f"/api/groups/{group_id}/join",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    # Учитель создаёт задание
    assignment_response = await client.post(f"/api/assignments/{group_id}", json={
        "title": "Math Homework",
        "description": "Solve problems 1-10",
        "due_date": None
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    assignment_id = assignment_response.json()["id"]

    # Студент сдаёт задание
    response = await client.post(f"/api/assignments/{assignment_id}/submit", json={
        "content": "My homework answers: 1, 2, 3..."
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_student_cannot_submit_twice(client, redis_store):
    teacher_token = await register_and_login(client, "teacher@example.com", "teacher", redis_store)
    student_token = await register_and_login(client, "student@example.com", "student", redis_store)

    group_response = await client.post("/api/groups/", json={
        "name": "Math Group",
        "subject": "Math",
        "tutor_name": "Mr. Smith",
        "description": "Advanced math group",
        "capacity": 10,
        "is_private": False,
        "group_type": "student"
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    group_id = group_response.json()["id"]

    await client.post(f"/api/groups/{group_id}/join",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assignment_response = await client.post(f"/api/assignments/{group_id}", json={
        "title": "Math Homework",
        "description": "Solve problems 1-10",
        "due_date": None
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    assignment_id = assignment_response.json()["id"]

    # Первая сдача
    await client.post(f"/api/assignments/{assignment_id}/submit", json={
        "content": "First submission"
    }, headers={"Authorization": f"Bearer {student_token}"})

    # Вторая сдача — должен быть 409
    response = await client.post(f"/api/assignments/{assignment_id}/submit", json={
        "content": "Second submission"
    }, headers={"Authorization": f"Bearer {student_token}"})
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_teacher_cannot_submit(client, redis_store):
    teacher_token = await register_and_login(client, "teacher@example.com", "teacher", redis_store)

    group_response = await client.post("/api/groups/", json={
        "name": "Math Group",
        "subject": "Math",
        "tutor_name": "Mr. Smith",
        "description": "Advanced math group",
        "capacity": 10,
        "is_private": False,
        "group_type": "student"
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    group_id = group_response.json()["id"]

    assignment_response = await client.post(f"/api/assignments/{group_id}", json={
        "title": "Math Homework",
        "description": "Solve problems 1-10",
        "due_date": None
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    assignment_id = assignment_response.json()["id"]

    # Учитель пытается сдать — должен быть 403
    response = await client.post(f"/api/assignments/{assignment_id}/submit", json={
        "content": "Teacher submission"
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    assert response.status_code == 403