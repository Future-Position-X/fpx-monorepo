from conftest import UUID_ZERO


def user_attributes():
    return {"email": "apitester@fpx.se", "password": "testing"}


def test_user_creation(client):
    res = client.post("/users", json=user_attributes())
    assert res.status_code == 201
    assert "apitester@fpx.se" in str(res.data)

    res = client.post("/sessions", json=user_attributes())
    assert res.status_code == 201
    assert "token" in str(res.data)


def test_user_creation_transaction_rollback(client, user):
    res = client.post(
        "/users", json={"email": user["email"], "password": user["password"]}
    )
    assert res.status_code == 400

    res = client.get("/providers")
    assert res.status_code == 200
    assert "test-user@test.se" not in str(res.data)


def test_user_creation_errors(client, user):
    res = client.post("/users", json=user_attributes())
    assert res.status_code == 201
    res = client.post("/users", json=user_attributes())
    assert res.status_code == 400


def test_get_users(client, user):
    res = client.get("/users")
    assert res.status_code == 200
    assert "test-user" in str(res.data)


def test_get_user(client, user):
    res = client.get("/users/{}".format(user["uuid"]))
    assert res.status_code == 200
    assert "test-user" in str(res.data)


def test_get_non_existing_user(client, user):
    res = client.get("/users/{}".format(UUID_ZERO))
    assert res.status_code == 404


def test_update_user(client, user):
    res = client.post(
        "/sessions", json={"email": "test-user@test.se", "password": "testing"}
    )
    assert res.status_code == 401
    assert "" in str(res.data)

    res = client.put("/users/{}".format(user["uuid"]), json=user_attributes())
    assert res.status_code == 204
    assert "" in str(res.data)

    res = client.post(
        "/sessions", json={"email": "test-user@test.se", "password": "testing"}
    )
    assert res.status_code == 201
    assert "token" in str(res.data)


def test_update_non_existing_user(client, user):
    res = client.put("/users/{}".format(UUID_ZERO), json=user_attributes())
    assert res.status_code == 404


def test_del_user(client, user):
    res = client.get("/users/{}".format(user["uuid"]))
    assert res.status_code == 200
    assert "test-user" in str(res.data)

    res = client.delete("/users/{}".format(user["uuid"]))
    assert res.status_code == 204

    res = client.get("/users/{}".format(user["uuid"]))
    assert res.status_code == 404
    assert "" in str(res.data)


def test_get_user_uuid(client, user):
    res = client.get("/users/uuid")
    assert res.status_code == 200
    assert str(user["uuid"]) in str(res.data)
