import pytest
from rest_framework.test import APIClient

from account.models import User, Profile
from page.models import Page, Post, Tag


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    user = User.objects.create(
        email="laegolas_best@example.mail",
        role="user",
        username="LaegolasSindarin",
    )
    user.set_password("some_pass")
    user.save()
    return user


@pytest.fixture
def admin():
    admin = User.objects.create(
        email="admin@example.mail",
        role=User.Roles.ADMIN,
        username="admin",
    )
    admin.set_password("admin_pass")
    admin.save()
    return admin


@pytest.fixture
def moderator():
    moderator = User.objects.create(
        email="moderator@example.mail",
        role=User.Roles.MODERATOR,
        username="moderator",
    )
    moderator.set_password("moderator_pass")
    moderator.save()
    return moderator


@pytest.fixture
def profile(user):
    profile = Profile.objects.create(
        user=user,
        bio="Update your profile",
        avatar=None
    )
    return profile


@pytest.fixture
def logged_in_client(user, client):
    client.post("api/login/", dict(email="laegolas_best@example.mail", password="some_pass", ))
    return client


@pytest.fixture
def access_token(user, client):
    request = client.post("/api/token/", dict(email="laegolas_best@example.mail", password="some_pass"))
    return request.data["access"]


@pytest.fixture
def access_token_admin(admin, client):
    request = client.post("/api/token/", dict(email="admin@example.mail", password="admin_pass"))
    return request.data["access"]



