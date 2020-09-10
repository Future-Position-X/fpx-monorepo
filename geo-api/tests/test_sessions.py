def test_create_session(anon_client):
    res = anon_client.post(
        "/sessions", json={"email": "test-user1@test.se", "password": "test"}
    )
    assert res.status_code == 201


def test_create_session_wrong_password(anon_client):
    res = anon_client.post(
        "/sessions", json={"email": "test-user1@test.se", "password": "wrong password"}
    )
    assert res.status_code == 401
