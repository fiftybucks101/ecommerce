from app.users.models import User


# --------------------------------------------------
# 1. User creation (POST /users/)
# --------------------------------------------------

def test_create_user_success(client):
    payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "password": "securepassword123",
    }

    response = client.post("/users/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Alice Smith"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "customer"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_cannot_create_user_with_duplicate_email(client, test_user):
    payload = {
        "name": "Duplicate User",
        "email": test_user.email,
        "password": "anotherpassword123",
    }

    response = client.post("/users/", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "A user with this email already exists."


def test_cannot_create_user_with_invalid_email(client):
    payload = {
        "name": "Invalid Email User",
        "email": "not-an-email",
        "password": "password123",
    }

    response = client.post("/users/", json=payload)

    assert response.status_code == 422


def test_cannot_create_user_with_short_password(client):
    payload = {
        "name": "Short Password User",
        "email": "short@example.com",
        "password": "short",  # Min length is 8
    }

    response = client.post("/users/", json=payload)

    assert response.status_code == 422


def test_cannot_create_user_missing_required_fields(client):
    response_no_email = client.post(
        "/users/",
        json={"name": "No Email", "password": "password123"},
    )
    assert response_no_email.status_code == 422

    response_no_password = client.post(
        "/users/",
        json={"name": "No Password", "email": "nopass@example.com"},
    )
    assert response_no_password.status_code == 422

    response_no_name = client.post(
        "/users/",
        json={"email": "noname@example.com", "password": "password123"},
    )
    assert response_no_name.status_code == 422


# --------------------------------------------------
# 2. User retrieval (GET /users/ and GET /users/{id})
# --------------------------------------------------

def test_get_users_empty(client):
    response = client.get("/users/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_users_list(client, test_user):
    response = client.get("/users/")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_user.id
    assert data[0]["email"] == test_user.email
    assert data[0]["role"] == test_user.role


def test_get_users_pagination(client, db_session):
    users = [
        User(
            name=f"User {i}",
            email=f"user{i}@example.com",
            password_hash="hash",
            role="customer",
        )
        for i in range(1, 6)
    ]
    db_session.add_all(users)
    db_session.flush()

    # Skip 0, limit 2
    res_page1 = client.get("/users/?skip=0&limit=2")
    assert res_page1.status_code == 200
    data1 = res_page1.json()
    assert len(data1) == 2

    # Skip 2, limit 2
    res_page2 = client.get("/users/?skip=2&limit=2")
    assert res_page2.status_code == 200
    data2 = res_page2.json()
    assert len(data2) == 2

    # Ensure pages contain distinct users
    ids1 = [u["id"] for u in data1]
    ids2 = [u["id"] for u in data2]
    assert set(ids1).isdisjoint(set(ids2))


def test_get_user_by_id_success(client, test_user):
    response = client.get(f"/users/{test_user.id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_user.id
    assert data["name"] == test_user.name
    assert data["email"] == test_user.email
    assert data["role"] == test_user.role


def test_get_user_by_id_not_found(client):
    response = client.get("/users/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


# --------------------------------------------------
# 3. User update (PUT /users/{id})
# --------------------------------------------------

def test_update_user_name_only(client, test_user):
    response = client.put(
        f"/users/{test_user.id}",
        json={"name": "Updated Customer Name"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_user.id
    assert data["name"] == "Updated Customer Name"
    assert data["email"] == test_user.email


def test_update_user_email_only(client, test_user):
    response = client.put(
        f"/users/{test_user.id}",
        json={"email": "newemail@example.com"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == "newemail@example.com"
    assert data["name"] == test_user.name


def test_update_user_both_name_and_email(client, test_user):
    response = client.put(
        f"/users/{test_user.id}",
        json={
            "name": "Completely New Name",
            "email": "completelynew@example.com",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_user.id
    assert data["name"] == "Completely New Name"
    assert data["email"] == "completelynew@example.com"


def test_update_user_with_same_email(client, test_user):
    response = client.put(
        f"/users/{test_user.id}",
        json={
            "name": "New Name Same Email",
            "email": test_user.email,
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == test_user.email


def test_cannot_update_user_to_existing_duplicate_email(client, db_session, test_user):
    other_user = User(
        name="Other User",
        email="other@example.com",
        password_hash="hash",
        role="customer",
    )
    db_session.add(other_user)
    db_session.flush()

    response = client.put(
        f"/users/{test_user.id}",
        json={"email": other_user.email},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "A user with this email already exists."


def test_cannot_update_nonexistent_user(client):
    response = client.put(
        "/users/99999",
        json={"name": "Ghost User"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


def test_cannot_update_user_with_invalid_email(client, test_user):
    response = client.put(
        f"/users/{test_user.id}",
        json={"email": "not-valid-email"},
    )

    assert response.status_code == 422


# --------------------------------------------------
# 4. User deletion (DELETE /users/{id})
# --------------------------------------------------

def test_delete_user_success(client, test_user):
    delete_res = client.delete(f"/users/{test_user.id}")

    assert delete_res.status_code == 204

    # Confirm user is removed from database
    get_res = client.get(f"/users/{test_user.id}")
    assert get_res.status_code == 404


def test_cannot_delete_nonexistent_user(client):
    response = client.delete("/users/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."

