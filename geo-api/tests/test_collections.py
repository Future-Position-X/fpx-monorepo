import json


def item_attributes():
    return {
        'geometry': 'POINT(1 1)',
        'properties': {
            'name': 'somename',
        },
    }


def collection_attributes():
    return {'name': 'gg', 'is_public': True}


def test_collection_creation(client):
    res = client.post('/collections', json=collection_attributes())
    assert res.status_code == 201
    assert ('gg' in str(res.data))


def test_api_can_get_all_public_collection(anon_client, collection, collection_private):
    res = anon_client.get('/collections')
    assert res.status_code == 200
    assert (collection['name'] in str(res.data))
    assert (collection_private['name'] not in str(res.data))

def test_api_can_get_private_collection(client, collection, collection_private):
    res = client.get('/collections')
    assert res.status_code == 200
    assert (collection['name'] in str(res.data))
    assert (collection_private['name'] in str(res.data))

def test_api_can_get_collection_by_uuid(client, collection):
    result = client.get(
        '/collections/{}'.format(collection['uuid']))
    assert result.status_code == 200
    assert (collection['name'] in str(result.data))


def test_collection_can_be_edited(client, collection):
    rv = client.put(
        '/collections/{}'.format(collection['uuid']),
        json={
            "name": "solo",
            "is_public": True,
        })
    assert rv.status_code == 200
    results = client.get('/collections/{}'.format(collection['uuid']))
    assert 'solo' in str(results.data)


def test_empty_collection_deletion(client, collection_empty):
    res = client.delete('/collections/{}'.format(collection_empty['uuid']))
    assert res.status_code == 204
    result = client.get('/collections/{}'.format(collection_empty['uuid']))
    assert result.status_code == 404


def test_collection_can_be_copied_to_new_collection(client, collection, collection_empty, item):
    res = client.post(
        '/collections/{}/copy'.format(collection['uuid']))
    assert res.status_code == 201
    collection_hash = json.loads(res.data.decode('utf-8'))

    result = client.get(
        '/collections/{}/items'.format(collection_hash['uuid']))
    assert result.status_code == 200
    assert (item['properties']['name'] in str(result.data))
    assert (str(item['uuid']) not in str(result.data))


def test_collection_can_be_copied_to_other_collection(client, collection, collection_empty, item):
    res = client.post(
        '/collections/{}/copy/{}'.format(collection['uuid'], collection_empty['uuid']), data=None)
    assert res.status_code == 201
    collection_hash = json.loads(res.data.decode('utf-8'))

    assert str(collection_empty['uuid']) == collection_hash['uuid']

    result = client.get(
        '/collections/{}/items'.format(collection_empty['uuid']))
    assert result.status_code == 200
    assert (item['properties']['name'] in str(result.data))
    assert (str(item['uuid']) not in str(result.data))
