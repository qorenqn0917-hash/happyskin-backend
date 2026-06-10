"""
인증 엔드포인트 테스트
- POST /api/v1/auth/signup
- POST /api/v1/auth/login
- GET  /api/v1/auth/me
"""

import pytest
from httpx import ASGITransport, AsyncClient


# API 키 없이 auth 전용 클라이언트
@pytest.fixture
async def auth_client():
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


SIGNUP_PAYLOAD = {
    "name": "테스트유저",
    "email": "test@example.com",
    "password": "password123",
    "password_confirm": "password123",
}


# ── 회원가입 ────────────────────────────────────────────────

@pytest.mark.anyio
async def test_signup_success(auth_client):
    response = await auth_client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body
    assert body["email"] == SIGNUP_PAYLOAD["email"]
    assert body["name"] == SIGNUP_PAYLOAD["name"]
    assert "user_id" in body


@pytest.mark.anyio
async def test_signup_duplicate_email(auth_client):
    await auth_client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    response = await auth_client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    assert response.status_code == 409
    assert "이미 사용 중인 이메일" in response.json()["detail"]


@pytest.mark.anyio
async def test_signup_password_too_short(auth_client):
    payload = {**SIGNUP_PAYLOAD, "password": "short", "password_confirm": "short"}
    response = await auth_client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_signup_password_mismatch(auth_client):
    payload = {**SIGNUP_PAYLOAD, "password_confirm": "different123"}
    response = await auth_client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_signup_empty_name(auth_client):
    payload = {**SIGNUP_PAYLOAD, "name": "   "}
    response = await auth_client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_signup_invalid_email(auth_client):
    payload = {**SIGNUP_PAYLOAD, "email": "not-an-email"}
    response = await auth_client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422


# ── 로그인 ──────────────────────────────────────────────────

@pytest.mark.anyio
async def test_login_success(auth_client):
    await auth_client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": SIGNUP_PAYLOAD["email"], "password": SIGNUP_PAYLOAD["password"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["email"] == SIGNUP_PAYLOAD["email"]


@pytest.mark.anyio
async def test_login_wrong_password(auth_client):
    await auth_client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": SIGNUP_PAYLOAD["email"], "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "비밀번호" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_nonexistent_email(auth_client):
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    assert response.status_code == 401


# ── 내 정보 조회 ─────────────────────────────────────────────

@pytest.mark.anyio
async def test_me_success(auth_client):
    me_payload = {**SIGNUP_PAYLOAD, "email": "me_test@example.com"}
    signup_res = await auth_client.post("/api/v1/auth/signup", json=me_payload)
    token = signup_res.json()["access_token"]

    response = await auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == me_payload["email"]
    assert body["name"] == me_payload["name"]
    assert "user_id" in body
    assert "created_at" in body


@pytest.mark.anyio
async def test_me_no_token(auth_client):
    response = await auth_client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_me_invalid_token(auth_client):
    response = await auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalidtoken.abc.xyz"},
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_me_malformed_header(auth_client):
    response = await auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "NotBearer sometoken"},
    )
    assert response.status_code == 401
