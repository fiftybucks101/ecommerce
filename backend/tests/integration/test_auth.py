from datetime import datetime, timedelta, timezone
from decimal import Decimal

import jwt

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    get_secret_key,
    hash_password,
    verify_password,
)
from app.users.models import User


# --------------------------------------------------
# 1. User registration (POST /auth/register)
# --------------------------------------------------

def test_register_success(client, db_session):
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "strongpassword123",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Jane Doe"
    assert data["email"] == "jane@example.com"
    assert data["role"] == "customer"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "password" not in data
    assert "password_hash" not in data

    # Verify user exists in database and password is truly hashed
    db_user = db_session.get(User, data["id"])
    assert db_user is not None
    assert db_user.password_hash != "strongpassword123"
    assert verify_password("strongpassword123", db_user.password_hash) is True


def test_register_normalizes_email_to_lowercase(client, db_session):
    payload = {
        "name": "Case Test",
        "email": "CaseUser@Example.COM",
        "password": "strongpassword123",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    assert response.json()["email"] == "caseuser@example.com"


def test_register_duplicate_email_conflict(client):
    payload = {
        "name": "First Registration",
        "email": "unique@example.com",
        "password": "strongpassword123",
    }

    res1 = client.post("/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt to register identical email
    res2 = client.post("/auth/register", json=payload)
    assert res2.status_code == 409
    assert "already registered" in res2.json()["detail"].lower()


def test_register_case_insensitive_duplicate_email(client):
    payload1 = {
        "name": "Lower Email",
        "email": "shared@example.com",
        "password": "strongpassword123",
    }
    res1 = client.post("/auth/register", json=payload1)
    assert res1.status_code == 201

    payload2 = {
        "name": "Upper Email",
        "email": "SHARED@EXAMPLE.COM",
        "password": "strongpassword123",
    }
    res2 = client.post("/auth/register", json=payload2)
    assert res2.status_code == 409


def test_register_invalid_email_format(client):
    payload = {
        "name": "Bad Email",
        "email": "invalid-email-address",
        "password": "strongpassword123",
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_register_password_too_short(client):
    payload = {
        "name": "Short Password",
        "email": "shortpass@example.com",
        "password": "short",  # Min length is 8
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_register_empty_name(client):
    payload = {
        "name": "",
        "email": "emptyname@example.com",
        "password": "strongpassword123",
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_register_missing_fields(client):
    response_no_pass = client.post(
        "/auth/register",
        json={"name": "No Pass", "email": "nopass@example.com"},
    )
    assert response_no_pass.status_code == 422

    response_no_email = client.post(
        "/auth/register",
        json={"name": "No Email", "password": "password123"},
    )
    assert response_no_email.status_code == 422


# --------------------------------------------------
# 2. User login (POST /auth/login)
# --------------------------------------------------

def test_login_success(client, db_session):
    # Setup registered user with hashed password
    user = User(
        name="Login User",
        email="loginuser@example.com",
        password_hash=hash_password("mypassword123"),
        role="customer",
    )
    db_session.add(user)
    db_session.flush()

    response = client.post(
        "/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "mypassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Decode and verify token claims
    payload = jwt.decode(
        data["access_token"],
        get_secret_key(),
        algorithms=[ALGORITHM],
    )
    assert payload["sub"] == str(user.id)
    assert "exp" in payload
    assert "iat" in payload


def test_login_case_insensitive_email(client, db_session):
    user = User(
        name="Case User",
        email="caseuser@example.com",
        password_hash=hash_password("password123"),
        role="customer",
    )
    db_session.add(user)
    db_session.flush()

    # Login with uppercase email
    response = client.post(
        "/auth/login",
        json={
            "email": "CASEUSER@EXAMPLE.COM",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_fails(client, db_session):
    user = User(
        name="User",
        email="wrongpass@example.com",
        password_hash=hash_password("correctpassword"),
        role="customer",
    )
    db_session.add(user)
    db_session.flush()

    response = client.post(
        "/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "incorrectpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
    assert "WWW-Authenticate" in response.headers


def test_login_nonexistent_email_fails(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_invalid_email_format(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "not-valid-format",
            "password": "password123",
        },
    )

    assert response.status_code == 422


# --------------------------------------------------
# 3. Authenticated profile (GET /auth/me)
# --------------------------------------------------

def test_get_me_success(client, db_session):
    user = User(
        name="Token User",
        email="tokenuser@example.com",
        password_hash=hash_password("password123"),
        role="customer",
    )
    db_session.add(user)
    db_session.flush()

    token = create_access_token(user.id)

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["name"] == "Token User"
    assert data["email"] == "tokenuser@example.com"
    assert data["role"] == "customer"


def test_get_me_unauthenticated_fails(client):
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing authentication token."


def test_get_me_malformed_token_fails(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-valid-jwt-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing authentication token."


def test_get_me_expired_token_fails(client, db_session):
    user = User(
        name="Expired User",
        email="expired@example.com",
        password_hash=hash_password("password123"),
        role="customer",
    )
    db_session.add(user)
    db_session.flush()

    # Generate an expired token (expired 10 minutes ago)
    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": str(user.id),
        "iat": now - timedelta(minutes=20),
        "exp": now - timedelta(minutes=10),
    }
    expired_token = jwt.encode(
        expired_payload,
        get_secret_key(),
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing authentication token."


def test_get_me_wrong_secret_key_fails(client, db_session):
    user = User(
        name="Hacked Token User",
        email="hacked@example.com",
        password_hash=hash_password("password123"),
        role="customer",
    )
    db_session.add(user)
    db_session.flush()

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "iat": now,
        "exp": now + timedelta(minutes=30),
    }
    fraudulent_token = jwt.encode(
        payload,
        "completely_wrong_secret_key_12345",
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {fraudulent_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing authentication token."


def test_get_me_deleted_user_token_fails(client, db_session):
    # Token for user ID that does not exist in the database
    token = create_access_token(user_id=999999)

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing authentication token."


# --------------------------------------------------
# 4. End-to-end authentication workflow
# --------------------------------------------------

def test_full_auth_lifecycle(client):
    # 1. Register new user
    register_res = client.post(
        "/auth/register",
        json={
            "name": "Full Flow User",
            "email": "fullflow@example.com",
            "password": "supersecurepassword123",
        },
    )
    assert register_res.status_code == 201
    user_id = register_res.json()["id"]

    # 2. Login with credentials
    login_res = client.post(
        "/auth/login",
        json={
            "email": "fullflow@example.com",
            "password": "supersecurepassword123",
        },
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token

    # 3. Access protected /auth/me endpoint using token
    me_res = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["id"] == user_id
    assert me_data["email"] == "fullflow@example.com"
    assert me_data["name"] == "Full Flow User"
    assert me_data["role"] == "customer"

