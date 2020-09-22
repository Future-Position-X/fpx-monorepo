# from typing import Dict

# from fastapi.testclient import TestClient
# from sqlalchemy.orm import Session

# from app import crud
# from app.core.config import settings
# from app.schemas.user import UserCreate
# from app.tests.utils.utils import random_email, random_lower_string


# def test_get_users_superuser_me(
#     client: TestClient, superuser_token_headers: Dict[str, str]
# ) -> None:
#     r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
#     current_user = r.json()
#     assert current_user
#     assert current_user["is_active"] is True
#     assert current_user["is_superuser"]
#     assert current_user["email"] == settings.FIRST_SUPERUSER


# def test_get_users_normal_user_me(
#     client: TestClient, normal_user_token_headers: Dict[str, str]
# ) -> None:
#     r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
#     current_user = r.json()
#     assert current_user
#     assert current_user["is_active"] is True
#     assert current_user["is_superuser"] is False
#     assert current_user["email"] == settings.EMAIL_TEST_USER


# def test_create_user_new_email(
#     client: TestClient, superuser_token_headers: dict, db: Session
# ) -> None:
#     username = random_email()
#     password = random_lower_string()
#     data = {"email": username, "password": password}
#     r = client.post(
#         f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data,
#     )
#     assert 200 <= r.status_code < 300
#     created_user = r.json()
#     user = crud.user.get_by_email(db, email=username)
#     assert user
#     assert user.email == created_user["email"]


# def test_get_existing_user(
#     client: TestClient, superuser_token_headers: dict, db: Session
# ) -> None:
#     username = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=username, password=password)
#     user = crud.user.create(db, obj_in=user_in)
#     user_id = user.id
#     r = client.get(
#         f"{settings.API_V1_STR}/users/{user_id}", headers=superuser_token_headers,
#     )
#     assert 200 <= r.status_code < 300
#     api_user = r.json()
#     existing_user = crud.user.get_by_email(db, email=username)
#     assert existing_user
#     assert existing_user.email == api_user["email"]


# def test_create_user_existing_username(
#     client: TestClient, superuser_token_headers: dict, db: Session
# ) -> None:
#     username = random_email()
#     # username = email
#     password = random_lower_string()
#     user_in = UserCreate(email=username, password=password)
#     crud.user.create(db, obj_in=user_in)
#     data = {"email": username, "password": password}
#     r = client.post(
#         f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data,
#     )
#     created_user = r.json()
#     assert r.status_code == 400
#     assert "_id" not in created_user


# def test_create_user_by_normal_user(
#     client: TestClient, normal_user_token_headers: Dict[str, str]
# ) -> None:
#     username = random_email()
#     password = random_lower_string()
#     data = {"email": username, "password": password}
#     r = client.post(
#         f"{settings.API_V1_STR}/users/", headers=normal_user_token_headers, json=data,
#     )
#     assert r.status_code == 400


# def test_retrieve_users(
#     client: TestClient, superuser_token_headers: dict, db: Session
# ) -> None:
#     username = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=username, password=password)
#     crud.user.create(db, obj_in=user_in)

#     username2 = random_email()
#     password2 = random_lower_string()
#     user_in2 = UserCreate(email=username2, password=password2)
#     crud.user.create(db, obj_in=user_in2)

#     r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
#     all_users = r.json()

#     assert len(all_users) > 1
#     for item in all_users:
#         assert "email" in item


from app.core.config import settings
from app.tests.conftest import UUID_ZERO


def user_attributes():
    return {"email": "apitester@fpx.se", "password": "testing"}


def test_user_creation(client):
    res = client.post(f'{settings.API_V1_STR}/users', json=user_attributes())
    assert res.status_code == 201
    assert "apitester@fpx.se" in str(res.content)

    res = client.post(f'{settings.API_V1_STR}/sessions', json=user_attributes())
    assert res.status_code == 201
    assert "token" in str(res.content)


def test_user_creation_transaction_rollback(client, user):
    res = client.post(
        f'{settings.API_V1_STR}/users', json={"email": user["email"], "password": user["password"]}
    )
    assert res.status_code == 400

    res = client.get(f'{settings.API_V1_STR}/providers')
    assert res.status_code == 200
    assert "test-user@test.se" not in str(res.content)


def test_user_creation_errors(client, user):
    res = client.post(f'{settings.API_V1_STR}/users', json=user_attributes())
    assert res.status_code == 201
    res = client.post(f'{settings.API_V1_STR}/users', json=user_attributes())
    assert res.status_code == 400


def test_get_users(client, user):
    res = client.get(f'{settings.API_V1_STR}/users')
    assert res.status_code == 200
    assert "test-user" in str(res.content)


def test_get_user(client, user):
    res = client.get(f'{settings.API_V1_STR}/users/{user["uuid"]}')
    assert res.status_code == 200
    assert "test-user" in str(res.content)


def test_get_non_existing_user(client, user):
    res = client.get(f'{settings.API_V1_STR}/users/{UUID_ZERO}')
    assert res.status_code == 404


def test_update_user(client, user):
    res = client.post(
        f'{settings.API_V1_STR}/sessions', json={"email": "test-user1@test.se", "password": "testing"}
    )
    assert res.status_code == 401
    assert "" in str(res.content)

    res = client.put(f'{settings.API_V1_STR}/users/{user["uuid"]}', json=user_attributes())
    assert res.status_code == 204
    assert "" in str(res.content)

    res = client.post(
        f'{settings.API_V1_STR}/sessions', json={"email": "test-user1@test.se", "password": "testing"}
    )
    assert res.status_code == 201
    assert "token" in str(res.content)


def test_update_non_existing_user(client, user):
    res = client.put(f'{settings.API_V1_STR}/users/{UUID_ZERO}', json=user_attributes())
    assert res.status_code == 404


def test_del_user(client, user):
    res = client.get(f'{settings.API_V1_STR}/users/{user["uuid"]}')
    assert res.status_code == 200
    assert "test-user" in str(res.content)

    res = client.delete(f'{settings.API_V1_STR}/users/{user["uuid"]}')
    assert res.status_code == 204

    res = client.get(f'{settings.API_V1_STR}/users/{user["uuid"]}')
    assert res.status_code == 404
    assert "" in str(res.content)


def test_get_user_uuid(client, user):
    res = client.get(f'{settings.API_V1_STR}/users/uuid')
    assert res.status_code == 200
    assert str(user["uuid"]) in str(res.content)
