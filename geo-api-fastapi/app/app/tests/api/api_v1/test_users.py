from app.core.config import settings

# from app.tests.conftest import UUID_ZERO


def user_attributes():
    return {"email": "apitester@fpx.se", "password": "testing"}


def test_user_creation(client):
    res = client.post(f"{settings.API_V1_STR}/users", json=user_attributes())
    assert res.status_code == 201
    assert "apitester@fpx.se" in str(res.content)

    res = client.post(f"{settings.API_V1_STR}/sessions", json=user_attributes())
    assert res.status_code == 201
    assert "token" in str(res.content)


def test_user_creation_transaction_rollback(client, user):
    res = client.post(
        f"{settings.API_V1_STR}/users",
        json={"email": user["email"], "password": user["password"]},
    )
    assert res.status_code == 409

    res = client.get(f"{settings.API_V1_STR}/providers")
    assert res.status_code == 200
    assert "test-user@test.se" not in str(res.content)


def test_user_creation_errors(client, user):
    res = client.post(f"{settings.API_V1_STR}/users", json=user_attributes())
    assert res.status_code == 201
    res = client.post(f"{settings.API_V1_STR}/users", json=user_attributes())
    assert res.status_code == 409


# def test_get_users(client, user):
#     res = client.get(f"{settings.API_V1_STR}/users")
#     assert res.status_code == 200
#     assert "test-user" in str(res.content)


def test_get_user(client, user):
    res = client.get(f'{settings.API_V1_STR}/users/{user["uuid"]}')
    assert res.status_code == 200
    assert "test-user" in str(res.content)


# def test_get_non_existing_user(client, user):
#     res = client.get(f"{settings.API_V1_STR}/users/{UUID_ZERO}")
#     assert res.status_code == 404


def test_update_user(client, user):
    res = client.post(
        f"{settings.API_V1_STR}/sessions",
        json={"email": "test-user1@test.se", "password": "testing"},
    )
    assert res.status_code == 401
    assert "" in str(res.content)

    res = client.put(
        f'{settings.API_V1_STR}/users/{user["uuid"]}', json=user_attributes()
    )
    assert res.status_code == 204
    assert "" in str(res.content)

    res = client.post(
        f"{settings.API_V1_STR}/sessions",
        json={"email": "test-user1@test.se", "password": "testing"},
    )
    assert res.status_code == 201
    assert "token" in str(res.content)


# def test_update_non_existing_user(client, user):
#     res = client.put(f"{settings.API_V1_STR}/users/{UUID_ZERO}", json=user_attributes())
#     assert res.status_code == 404


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
    res = client.get(f"{settings.API_V1_STR}/users/uuid")
    assert res.status_code == 200
    assert str(user["uuid"]) in str(res.content)
