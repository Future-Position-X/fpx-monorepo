import json

def user_attributes():
    return {'email': 'apitester@fpx.se', 'password': 'test'}


def test_user_creation(client):
    res = client.post('/users', json=user_attributes())
    assert res.status_code == 201
    assert ('apitester@fpx.se' in str(res.data))

