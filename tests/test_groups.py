import pytest
import json
from unittest.mock import patch


async def register_and_login(client, email, role, store):
    """Хелпер — регистрация и логин"""
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


@pytest.mark.asyncio
async def test_teacher_can_create_group(client, redis_store):
    token = await register_and_login(client, "teacher@example.com", "teacher", redis_store)
    response = await client.post("/api/groups/", json={
        "name": "Math Group",
        "subject": "Math",
        "tutor_name": "Mr. Smith",
        "description": "Advanced math group",
        "capacity": 10,
        "is_private": False
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_student_cannot_create_group(client, redis_store):
    token = await register_and_login(client, "student@example.com", "student", redis_store)
    response = await client.post("/api/groups/", json={
        "name": "Math Group",
        "subject": "Math",
        "tutor_name": "Mr. Smith",
        "description": "Advanced math group",
        "capacity": 10,
        "is_private": False
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_student_can_join_group(client, redis_store):
    teacher_token = await register_and_login(client, "teacher@example.com", "teacher", redis_store)
    student_token = await register_and_login(client, "student@example.com", "student", redis_store)

    group_response = await client.post("/api/groups/", json={
        "name": "Math Group",
        "subject": "Math",
        "tutor_name": "Mr. Smith",
        "description": "Advanced math group",
        "capacity": 10,
        "is_private": False
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    group_id = group_response.json()["id"]

    response = await client.post(f"/api/groups/{group_id}/join",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_student_cannot_join_twice(client, redis_store):
    teacher_token = await register_and_login(client, "teacher@example.com", "teacher", redis_store)
    student_token = await register_and_login(client, "student@example.com", "student", redis_store)

    group_response = await client.post("/api/groups/", json={
        "name": "Math Group",
        "subject": "Math",
        "tutor_name": "Mr. Smith",
        "description": "Advanced math group",
        "capacity": 10,
        "is_private": False
    }, headers={"Authorization": f"Bearer {teacher_token}"})
    group_id = group_response.json()["id"]

    await client.post(f"/api/groups/{group_id}/join",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    response = await client.post(f"/api/groups/{group_id}/join",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_student_can_leave_group(client, redis_store):
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

    response = await client.delete(f"/api/groups/{group_id}/leave",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_teacher_can_delete_own_group(client, redis_store):
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

    response = await client.delete(f"/api/groups/{group_id}",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_student_cannot_delete_group(client, redis_store):
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

    response = await client.delete(f"/api/groups/{group_id}",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 403