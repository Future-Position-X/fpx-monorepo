import json


def collection():
    return {
        'name': 'gg',
        'is_public': True
    }


def item():
    return {
        'geometry': 'POINT(1 1)',
        'properties': {
            'name': 'somename',
        },
    }


def test_item_creation(client):
    res = client.post('/collections', json=collection())
    assert res.status_code == 201
    collection_hash = json.loads(res.data.decode('utf-8'))

    res = client.get('/collections/{}'.format(collection_hash['uuid']))
    assert res.status_code == 200

    res = client.post('/collections/{}/items'.format(collection_hash['uuid']), json=item())
    assert res.status_code == 201
    item_hash = json.loads(res.data.decode('utf-8'))

    res = client.get(
        '/collections/{}/items/{}'.format(item_hash['collection_uuid'], item_hash['uuid']))

    assert res.status_code == 200
    print(res.data)
    assert ('somename' in str(res.data))


def test_get_items(client):
    res = client.post('/collections', json=collection())
    assert res.status_code == 201
    collection_hash = json.loads(res.data.decode('utf-8'))

    res = client.get('/collections/{}'.format(collection_hash['uuid']))
    assert res.status_code == 200

    res = client.post('/collections/{}/items'.format(collection_hash['uuid']), json=item())
    assert res.status_code == 201
    item_hash = json.loads(res.data.decode('utf-8'))

    res = client.get(
        '/collections/{}/items'.format(item_hash['collection_uuid']))

    assert res.status_code == 200
    assert ('somename' in str(res.data))


def test_item_creation_in_non_existent_collection(client):
    import uuid
    res = client.post('/collections/{}/items'.format(uuid.uuid4()), json=item())
    assert res.status_code == 404


def test_api_can_get_item_by_collection_uuid_and_uuid(client, collection):
    res = client.post('/collections/{}/items'.format(collection['uuid']), json=item())
    assert res.status_code == 201
    item_hash = json.loads(res.data.decode('utf-8'))

    res = client.get(
        '/collections/{}/items/{}'.format(item_hash['collection_uuid'], item_hash['uuid']))

    assert res.status_code == 200
    assert ('somename' in str(res.data))


def test_api_error_on_item_not_found(client, collection):
    res = client.get(
        '/collections/{}/items/{}'.format(collection['uuid'], collection['uuid']))

    assert res.status_code == 404

# def test_test(collection, session):
#     from app.models import Item
#     Item.set_session(session)
#
#     item = Item.create(geometry=None, properties={}, collection_uuid=collection['uuid'], provider_uuid=collection['provider_uuid'])
#     #Item.session.commit()
#     items=Item.find_by_collection_uuid(collection['uuid'], {'valid': None, 'offset': 0, 'limit': 10, 'property_filter': None})
#     print(items[0].to_dict())
#
#     #item2 = items[0]
#     #print(item2.provider_uuid)
