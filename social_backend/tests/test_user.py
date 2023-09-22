import pytest


@pytest.mark.django_db
def test_register_user(client):
    """Testing successful user registration"""

    payload = dict(
        username="Aragorn",
        email="aragorn_best@example.mail",
        password="sOmeP@ssWoRd1581",
        password_confirmation="sOmeP@ssWoRd1581"

    )
    response = client.post("/api/register/", payload)

    data = response.data

    assert response.status_code == 201
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "password" not in data
    assert "password_confirmation" not in data


@pytest.mark.django_db
def test_register_user_wrong_password_confirmation(client):
    """Testing registration with incorrect password confirmation"""
    payload = dict(
        username="Aragorn",
        email="aragorn_best@example.mail",
        password="sOmeP@ssWoRd1581",
        password_confirmation="WongPass"

    )

    response = client.post("/api/register/", payload)

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_user(client, user):
    """Successful login testing"""
    response = client.post("/api/login/", dict(email="laegolas_best@example.mail", password="some_pass", ))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_user_fail(client):
    """Login testing with incorrect password"""
    response = client.post("/api/login/", dict(email="laegolas_best@example.mail", password="wrong_pass", ))

    assert response.status_code == 400


@pytest.mark.django_db
def test_token_authentication(client, user):
    """Testing token authentication"""
    request = client.post("/api/token/", dict(email="laegolas_best@example.mail", password="some_pass"))

    assert "access" in request.data
    assert "refresh" in request.data


@pytest.mark.django_db
def test_retrieve_me(logged_in_client, access_token, user):
    """Testing users self information"""
    response = logged_in_client.get(f"/api/users/me/", HTTP_AUTHORIZATION=f"Bearer {access_token}")

    assert response.status_code == 200

    assert response.data["username"] == user.username
    assert response.data["email"] == user.email


@pytest.mark.django_db
def test_retrieve_user(logged_in_client, user):
    """Testing display users information per ID"""
    response = logged_in_client.get(f"/api/users/{user.id}/")

    assert response.status_code == 200

    assert response.data["username"] == user.username
    assert response.data["email"] == user.email


@pytest.mark.django_db
def test_get_user_profile(logged_in_client, access_token):
    """Testing user profile display"""
    request = logged_in_client.get("/api/profile/", HTTP_AUTHORIZATION=f"Bearer {access_token}")

    assert "bio" in request.data
    assert request.data.get("avatar") is None


@pytest.mark.django_db
def test_put_user_profile(logged_in_client, access_token):
    """Testing user profile changes"""
    request = logged_in_client.put("/api/profile/", {"bio": "New bio!"}, HTTP_AUTHORIZATION=f"Bearer {access_token}")

    assert request.data["bio"] == "New bio!"


@pytest.mark.django_db
def test_get_users_list(logged_in_client, access_token, user, admin, moderator):
    """Testing display list of all users"""
    request = logged_in_client.get("/api/users/", HTTP_AUTHORIZATION=f"Bearer {access_token}")

    assert len(request.data) == 3


@pytest.mark.django_db
def test_block_user_admin(client, access_token_admin, user, admin):
    """Testing user block with admin permissions"""
    client.post("/api/login/", dict(email="admin@example.mail", password="admin_pass"))
    response = client.put(f"/api/users/{user.id}/block/", HTTP_AUTHORIZATION=f"Bearer {access_token_admin}")

    assert response.status_code == 200
    assert response.data["detail"] == "User blocked successfully."


@pytest.mark.django_db
def test_unblock_user_admin(client, access_token_admin, user, admin):
    """Testing user unblock with admin permissions"""
    client.post("/api/login/", dict(email="admin@example.mail", password="admin_pass"))
    response = client.put(f"/api/users/{user.id}/unblock/", HTTP_AUTHORIZATION=f"Bearer {access_token_admin}")

    assert response.status_code == 200
    assert response.data["detail"] == "User unblocked successfully."


@pytest.mark.django_db
def test_block_user_without_permission(client, access_token, user, admin):
    """Testing user block without permissions"""
    client.post("/api/login/", dict(email="laegolas_best@example.mail", password="some_pass"))
    response = client.put(f"/api/users/{admin.id}/block/", HTTP_AUTHORIZATION=f"Bearer {access_token}")

    assert response.status_code == 403


@pytest.mark.django_db
def test_unblock_user_without_permission(client, access_token, user, admin):
    """Testing user unblock without permissions"""
    client.post("/api/login/", dict(email="laegolas_best@example.mail", password="some_pass"))
    response = client.put(f"/api/users/{admin.id}/unblock/", HTTP_AUTHORIZATION=f"Bearer {access_token}")

    assert response.status_code == 403





