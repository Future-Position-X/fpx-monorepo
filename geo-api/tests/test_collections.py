import json

def item_attributes():
    return {
        'geometry': None,
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


def test_api_can_get_all_public_collection(client):
    res = client.post('/collections', json=collection_attributes())
    assert res.status_code == 201
    res = client.get('/collections')
    assert res.status_code == 200
    assert ('gg' in str(res.data))


def test_api_can_get_collection_by_uuid(client):
    rv = client.post('/collections', json=collection_attributes())
    assert rv.status_code == 201
    result_in_json = json.loads(rv.data.decode('utf-8'))
    result = client.get(
        '/collections/{}'.format(result_in_json['uuid']))
    assert result.status_code == 200
    assert ('gg' in str(result.data))


def test_collection_can_be_edited(client):
    rv = client.post(
        '/collections',
        json=collection_attributes())
    assert rv.status_code == 201
    result_in_json = json.loads(rv.data.decode('utf-8'))
    rv = client.put(
        '/collections/{}'.format(result_in_json['uuid']),
        json={
            "name": "solo",
            "is_public": True,
        })
    assert rv.status_code == 200
    results = client.get('/collections/{}'.format(result_in_json['uuid']))
    assert 'solo' in str(results.data)


def test_collection_deletion(client):
    rv = client.post(
        '/collections',
        json=collection_attributes())
    assert rv.status_code == 201
    result_in_json = json.loads(rv.data.decode('utf-8'))
    res = client.delete('/collections/{}'.format(result_in_json['uuid']))
    assert res.status_code == 204
    result = client.get('/collections/{}'.format(result_in_json['uuid']))
    assert result.status_code == 404

def test_collection_can_be_copied_to_new_collection(client, collection):
    res = client.post('/collections/{}/items'.format(collection['uuid']), json=item_attributes())
    assert res.status_code == 201

    res = client.post(
        '/collections/{}/copy'.format(collection['uuid']))
    assert res.status_code == 201
    collection_hash = json.loads(res.data.decode('utf-8'))

    result = client.get(
        '/collections/{}/items'.format(collection_hash['uuid']))
    assert result.status_code == 200
    #collection_hash = json.loads(res.data.decode('utf-8'))
    #print(collection_hash)
    #assert ('somename' in str(result.data))


# def test_collection_can_be_copied_to_other_collection(client, collection):
#     res = client.post('/collections/{}/items'.format(collection['uuid']), json=item_attributes())
#     assert res.status_code == 201
#
#     res = client.post(
#         '/collections',
#         json={
#             "name": "othercollection",
#             "is_public": True,
#         })
#     assert res.status_code == 201
#     other_collection_hash = json.loads(res.data.decode('utf-8'))
#
#
#     res = client.post(
#         '/collections/{}/copy/{}'.format(collection['uuid'], other_collection_hash['uuid']), data=None)
#     assert res.status_code == 201
#     collection_hash = json.loads(res.data.decode('utf-8'))
#
#     assert other_collection_hash['uuid'] == collection_hash['uuid']
#
#     result = client.get(
#         '/collections/{}/items'.format(other_collection_hash['uuid']))
#     assert result.status_code == 200
#     assert ('somename' in str(result.data))



