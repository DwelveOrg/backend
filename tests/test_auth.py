import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_register_start(client):
    with patch("app.routers.auth.send_verification_email") as mock_email:
        mock_email.return_value = None
        response = await client.post("/api/auth/register/start", json={
            "full_name": "Test User",
            "email": "test@example.com",
            "role": "student"
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Verification code sent."


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    with patch("app.routers.auth.send_verification_email"):
        await client.post("/api/auth/register/start", json={
            "full_name": "Test User",
            "email": "test@example.com",
            "role": "student"
        })
        response = await client.post("/api/auth/register/start", json={
            "full_name": "Test User",
            "email": "test@example.com",
            "role": "student"
        })
        assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_verify_wrong_code(client):
    with patch("app.routers.auth.send_verification_email"):
        await client.post("/api/auth/register/start", json={
            "full_name": "Test User",
            "email": "test@example.com",
            "role": "student"
        })
        response = await client.post("/api/auth/register/verify", json={
            "email": "test@example.com",
            "code": "000000"
        })
        assert response.status_code == 400