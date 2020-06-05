import json



def collection():
    return {'name': 'gg', 'is_public': True}


def test_collection_creation(client):
    res = client.post('/collections', json=collection())
    assert res.status_code == 201
    assert ('gg' in str(res.data))

def test_api_can_get_all_public_collection(client):
    res = client.post('/collections', json=collection())
    assert res.status_code == 201
    res = client.get('/collections')
    assert res.status_code == 200
    assert ('gg' in str(res.data))

def test_api_can_get_collection_by_id(client):
    rv = client.post('/collections', json=collection())
    assert rv.status_code == 201
    result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
    result = client.get(
        '/collections/{}'.format(result_in_json['uuid']))
    assert result.status_code == 200
    assert ('gg' in str(result.data))


def test_collection_deletion(client):
    rv = client.post(
        '/collections',
        json={'name': 'yolo', 'is_public': True})
    assert rv.status_code == 201
    result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
    res = client.delete('/collections/{}'.format(result_in_json['uuid']))
    assert res.status_code == 204
    result = client.get('/collections/{}'.format(result_in_json['uuid']))
    assert result.status_code == 404
