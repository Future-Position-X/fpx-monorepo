import json
import uuid

import magic


def collection_attributes():
    return {
        'name': 'gg',
        'is_public': True
    }


def item_attributes():
    return {
        'geometry': 'POINT(1 1)',
        'properties': {
            'name': 'somename',
        },
    }


def item_attributes_geojson():
    return {
        "type": "FeatureCollection",
        "name": "TESTAREAS",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                16.9904,
                                60.6358
                            ],
                            [
                                16.9897,
                                60.6351
                            ],
                            [
                                16.9884,
                                60.6331
                            ],
                            [
                                16.9879,
                                60.6316
                            ],
                            [
                                16.9877,
                                60.6306
                            ],
                        ]
                    ]
                },
                "properties": {
                    "name": "somegeojson"
                }
            }
        ]
    }


def test_get_collection_item_json(client, item):
    res = client.get(
        '/collections/{}/items/{}'.format(item['collection_uuid'], item['uuid']),
        headers={'accept': 'application/json'})
    assert res.status_code == 200
    item_hash = json.loads(res.data.decode('utf-8'))

    assert {
               "uuid": str(item['uuid']),
               "collection_uuid": str(item['collection_uuid']),
               "geometry": {'type': 'Point', 'coordinates': [1.0, 1.0]},
               "properties": {
                   "name": "test-item"
               }
           }.items() <= item_hash.items()


def test_get_collection_item_json_404(client, item):
    res = client.get(
        '/collections/{}/items/{}'.format(item['collection_uuid'], uuid.uuid4()),
        headers={'accept': 'application/json'})
    assert res.status_code == 404
    assert ('not found' in str(res.data))


def test_get_collection_item_geojson(client, item):
    res = client.get(
        '/collections/{}/items/{}'.format(item['collection_uuid'], item['uuid']),
        headers={'accept': 'application/geojson'}, content_type='application/geojson')
    assert res.status_code == 200
    item_hash = json.loads(res.data.decode('utf-8'))

    assert {
               "type": "Feature",
               "geometry": {
                   "type": "Point",
                   "coordinates": [
                       1.0,
                       1.0
                   ]
               },
               "properties": {
                   "name": "test-item"
               }
           }.items() <= item_hash.items()


def test_get_collection_item_png(client, item):
    res = client.get(
        '/collections/{}/items/{}?map_id=transparent'.format(item['collection_uuid'], item['uuid']),
        headers={'accept': 'image/png'}, content_type='image/png')
    assert res.status_code == 200
    mime = magic.from_buffer(res.data, mime=True)
    assert mime == 'image/png'


def test_delete_collection_item(client, item):
    res = client.delete('/collections/{}/items/{}'.format(item['collection_uuid'], item['uuid']), headers={'accept': 'application/json'})
    assert res.status_code == 204

    res = client.get(
        '/items/{}'.format(item['uuid']),
        headers={'accept': 'application/json'})
    assert res.status_code == 404
    assert ('not found' in str(res.data))


def test_get_item_json(client, item):
    res = client.get(
        '/items/{}'.format(item['uuid']),
        headers={'accept': 'application/json'})
    assert res.status_code == 200
    item_hash = json.loads(res.data.decode('utf-8'))

    assert {
               "uuid": str(item['uuid']),
               "collection_uuid": str(item['collection_uuid']),
               "geometry": {'type': 'Point', 'coordinates': [1.0, 1.0]},
               "properties": {
                   "name": "test-item"
               }
           }.items() <= item_hash.items()


def test_get_item_json_404(client, item):
    res = client.get(
        '/items/{}'.format(uuid.uuid4()),
        headers={'accept': 'application/json'})
    assert res.status_code == 404
    assert ('not found' in str(res.data))


def test_get_item_geojson(client, item):
    res = client.get(
        '/items/{}'.format(item['uuid']),
        headers={'accept': 'application/geojson'}, content_type='application/geojson')
    assert res.status_code == 200
    item_hash = json.loads(res.data.decode('utf-8'))

    assert {
               "type": "Feature",
               "geometry": {
                   "type": "Point",
                   "coordinates": [
                       1.0,
                       1.0
                   ]
               },
               "properties": {
                   "name": "test-item"
               }
           }.items() <= item_hash.items()


def test_get_item_png(client, item):
    res = client.get(
        '/items/{}?map_id=transparent'.format(item['uuid']),
        headers={'accept': 'image/png'}, content_type='image/png')
    assert res.status_code == 200
    mime = magic.from_buffer(res.data, mime=True)
    assert mime == 'image/png'


def test_get_items(client, collection):
    res = client.get('/collections/{}/items'.format(collection['uuid']), headers={'accept': 'application/json'})
    assert res.status_code == 200
    assert not ('FeatureCollection' in str(res.data))
    assert ('test-item' in str(res.data))


def test_get_items_geojson(client, collection):
    res = client.get('/collections/{}/items'.format(collection['uuid']), headers={'accept': 'application/geojson'})
    assert res.status_code == 200
    assert ('FeatureCollection' in str(res.data))
    assert ('test-item' in str(res.data))


def test_get_items_png(client, collection):
    res = client.get('/collections/{}/items?map_id=transparent'.format(collection['uuid']),
                     headers={'accept': 'image/png'})
    assert res.status_code == 200
    mime = magic.from_buffer(res.data, mime=True)
    assert mime == 'image/png'


def test_get_items_by_name(client, collection):
    res = client.get('/collections/by_name/{}/items'.format(collection['name']), headers={'accept': 'application/json'})
    assert res.status_code == 200
    assert not ('FeatureCollection' in str(res.data))
    assert ('test-item' in str(res.data))


def test_get_items_by_name_geojson(client, collection):
    res = client.get('/collections/by_name/{}/items'.format(collection['name']),
                     headers={'accept': 'application/geojson'})
    assert res.status_code == 200
    assert ('FeatureCollection' in str(res.data))
    assert ('test-item' in str(res.data))


def test_get_items_by_name_png(client, collection):
    res = client.get('/collections/by_name/{}/items?map_id=transparent'.format(collection['name']),
                     headers={'accept': 'image/png'})
    assert res.status_code == 200
    mime = magic.from_buffer(res.data, mime=True)
    assert mime == 'image/png'


def test_item_creation(client):
    res = client.post('/collections', json=collection_attributes())
    assert res.status_code == 201
    collection_hash = json.loads(res.data.decode('utf-8'))

    res = client.get('/collections/{}'.format(collection_hash['uuid']))
    assert res.status_code == 200

    res = client.post('/collections/{}/items'.format(collection_hash['uuid']), json=item_attributes())
    assert res.status_code == 201
    item_hash = json.loads(res.data.decode('utf-8'))

    res = client.get(
        '/collections/{}/items/{}'.format(item_hash['collection_uuid'], item_hash['uuid']))

    assert res.status_code == 200
    assert ('somename' in str(res.data))


def test_item_creation_geojson(client, collection, item):
    res = client.post('/collections/{}/items'.format(collection['uuid']), json=item_attributes_geojson(),
                      headers={'accept': 'application/geojson', 'content-type': 'application/geojson'})
    assert res.status_code == 201
    items = json.loads(res.data.decode('utf-8'))

    assert len(items) == 1
    assert items[0]['uuid'] != item['uuid']

def test_item_delete(client, item):
    res = client.delete('/items/{}'.format(item['uuid']), headers={'accept': 'application/json'})
    assert res.status_code == 204

    res = client.get(
        '/items/{}'.format(item['uuid']),
        headers={'accept': 'application/json'})
    assert res.status_code == 404
    assert ('not found' in str(res.data))

def test_item_creation_in_non_existent_collection(client):
    import uuid
    res = client.post('/collections/{}/items'.format(uuid.uuid4()), json=item_attributes())
    assert res.status_code == 404


def test_api_can_get_item_by_collection_uuid_and_uuid(client, collection):
    res = client.post('/collections/{}/items'.format(collection['uuid']), json=item_attributes())
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
