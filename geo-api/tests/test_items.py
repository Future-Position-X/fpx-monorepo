import json
import uuid

import magic
import pytest

from conftest import UUID_ZERO


def collection_attributes():
    return {"name": "gg", "is_public": True}


def item_attributes():
    return {"geometry": "POINT(1 1)", "properties": {"name": "somename"}}


def item_attributes_empty_geometry():
    return {"geometry": None, "properties": {"name": "somenameempty"}}


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
                            [16.9904, 60.6358],
                            [16.9897, 60.6351],
                            [16.9884, 60.6331],
                            [16.9879, 60.6316],
                            [16.9877, 60.6306],
                        ]
                    ],
                },
                "properties": {"name": "somegeojson"},
            }
        ],
    }


def test_get_collection_item_json(client, item):
    res = client.get(
        "/collections/{}/items/{}".format(item["collection_uuid"], item["uuid"]),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    item_hash = json.loads(res.data.decode("utf-8"))

    assert {
        "uuid": str(item["uuid"]),
        "collection_uuid": str(item["collection_uuid"]),
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        "properties": {"name": "test-item1", "second_prop": "test-prop1"},
    }.items() <= item_hash.items()


def test_get_collection_item_json_404(client, item):
    res = client.get(
        "/collections/{}/items/{}".format(item["collection_uuid"], uuid.uuid4()),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 404
    assert "not found" in str(res.data)


def test_get_collection_item_geojson(client, item):
    res = client.get(
        "/collections/{}/items/{}".format(item["collection_uuid"], item["uuid"]),
        headers={"accept": "application/geojson"},
        content_type="application/geojson",
    )
    assert res.status_code == 200
    item_hash = json.loads(res.data.decode("utf-8"))

    assert {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        "properties": {"name": "test-item1", "second_prop": "test-prop1"},
    }.items() <= item_hash.items()


def test_get_collection_item_png(client, item):
    res = client.get(
        "/collections/{}/items/{}?map_id=transparent".format(
            item["collection_uuid"], item["uuid"]
        ),
        headers={"accept": "image/png"},
        content_type="image/png",
    )
    assert res.status_code == 200
    mime = magic.from_buffer(res.data, mime=True)
    assert mime == "image/png"


def test_delete_collection_item(client, item):
    res = client.delete(
        "/collections/{}/items/{}".format(item["collection_uuid"], item["uuid"]),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 204

    res = client.get(
        "/items/{}".format(item["uuid"]), headers={"accept": "application/json"}
    )
    assert res.status_code == 404
    assert "not found" in str(res.data)


def test_delete_collection_items(client, item):
    res = client.delete(
        "/collections/{}/items".format(item["collection_uuid"]),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 204

    res = client.get(
        "/items/{}".format(item["uuid"]), headers={"accept": "application/json"}
    )
    assert res.status_code == 404
    assert "not found" in str(res.data)


def test_get_item_json(client, item):
    res = client.get(
        "/items/{}".format(item["uuid"]), headers={"accept": "application/json"}
    )
    assert res.status_code == 200
    item_hash = json.loads(res.data.decode("utf-8"))

    assert {
        "uuid": str(item["uuid"]),
        "collection_uuid": str(item["collection_uuid"]),
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        "properties": {"name": "test-item1", "second_prop": "test-prop1"},
    }.items() <= item_hash.items()


def test_get_item_json_404(client, item):
    res = client.get(
        "/items/{}".format(uuid.uuid4()), headers={"accept": "application/json"}
    )
    assert res.status_code == 404
    assert "not found" in str(res.data)


def test_get_item_geojson(client, item):
    res = client.get(
        "/items/{}".format(item["uuid"]),
        headers={"accept": "application/geojson"},
        content_type="application/geojson",
    )
    assert res.status_code == 200
    item_hash = json.loads(res.data.decode("utf-8"))

    assert {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        "properties": {"name": "test-item1", "second_prop": "test-prop1"},
    }.items() <= item_hash.items()


def test_get_item_png(client, item):
    res = client.get(
        "/items/{}?map_id=transparent".format(item["uuid"]),
        headers={"accept": "image/png"},
        content_type="image/png",
    )
    assert res.status_code == 200
    mime = magic.from_buffer(res.data, mime=True)
    assert mime == "image/png"


def test_get_items(client, collection):
    res = client.get(
        "/collections/{}/items".format(collection["uuid"]),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.data))
    assert "test-item1" in str(res.data)
    assert "test-item-empty1" in str(res.data)

    res = client.get(
        "/collections/{}/items?valid=true".format(collection["uuid"]),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.data))
    assert "test-item1" in str(res.data)
    assert "test-item-empty1" not in str(res.data)


def test_get_shared_items(client, user2, client2, collection_private):
    res = client2.get(
        "/collections/{}/items".format(collection_private["uuid"]),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    items_array = json.loads(res.data.decode("utf-8"))
    assert len(items_array) == 0

    res = client.post(
        "/acls",
        json={
            "granted_provider_uuid": user2["provider_uuid"],
            "collection_uuid": collection_private["uuid"],
            "access": "read",
        },
        headers={"accept": "application/json"},
    )
    assert res.status_code == 201
    acl = json.loads(res.data.decode("utf-8"))

    res = client2.get(
        "/collections/{}/items".format(collection_private["uuid"]),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-private1" in str(res.data)

    res = client.delete(
        "/acls/{}".format(acl["uuid"]), headers={"accept": "application/json"}
    )
    assert res.status_code == 204

    res = client2.get(
        "/collections/{}/items".format(collection_private["uuid"]),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    items_array = json.loads(res.data.decode("utf-8"))
    assert len(items_array) == 0


def test_get_items_geojson(client, collection):
    res = client.get(
        "/collections/{}/items".format(collection["uuid"]),
        headers={"accept": "application/geojson"},
    )
    assert res.status_code == 200
    assert "FeatureCollection" in str(res.data)
    assert "test-item1" in str(res.data)
    # We can't represent empty geometry in a FeatureCollection
    assert "test-item-empty1" not in str(res.data)


def test_get_items_png(client, collection):
    res = client.get(
        "/collections/{}/items?map_id=transparent".format(collection["uuid"]),
        headers={"accept": "image/png"},
    )
    assert res.status_code == 200
    mime = magic.from_buffer(res.data, mime=True)
    assert mime == "image/png"


def test_get_items_by_name(client, collection):
    res = client.get(
        "/collections/by_name/{}/items".format(collection["name"]),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.data))
    assert "test-item1" in str(res.data)


def test_get_items_by_name_geojson(client, collection):
    res = client.get(
        "/collections/by_name/{}/items".format(collection["name"]),
        headers={"accept": "application/geojson"},
    )
    assert res.status_code == 200
    assert "FeatureCollection" in str(res.data)
    assert "test-item1" in str(res.data)


def test_get_items_by_name_png(client, collection):
    res = client.get(
        "/collections/by_name/{}/items?map_id=transparent".format(collection["name"]),
        headers={"accept": "image/png"},
    )
    assert res.status_code == 200
    mime = magic.from_buffer(res.data, mime=True)
    assert mime == "image/png"


def test_item_creation(client, collection):
    res = client.post(
        "/collections/{}/items".format(collection["uuid"]), json=item_attributes()
    )
    assert res.status_code == 201
    item_hash = json.loads(res.data.decode("utf-8"))

    res = client.get(
        "/collections/{}/items/{}".format(
            item_hash["collection_uuid"], item_hash["uuid"]
        )
    )
    assert res.status_code == 200
    assert "somename" in str(res.data)


def test_item_creation_empty_geom(client, collection):
    res = client.post(
        "/collections/{}/items".format(collection["uuid"]),
        json=item_attributes_empty_geometry(),
    )
    assert res.status_code == 201
    item_hash = json.loads(res.data.decode("utf-8"))

    res = client.get(
        "/collections/{}/items/{}".format(
            item_hash["collection_uuid"], item_hash["uuid"]
        )
    )

    assert res.status_code == 200
    assert "somenameempty" in str(res.data)


def test_item_creation_geojson(client, collection, item):
    res = client.post(
        "/collections/{}/items".format(collection["uuid"]),
        json=item_attributes_geojson(),
        headers={
            "accept": "application/geojson",
            "content-type": "application/geojson",
        },
    )
    assert res.status_code == 201
    items = json.loads(res.data.decode("utf-8"))

    assert len(items) == 1
    assert items[0]["uuid"] != item["uuid"]


def test_item_delete(client, item):
    res = client.delete(
        "/items/{}".format(item["uuid"]), headers={"accept": "application/json"}
    )
    assert res.status_code == 204

    res = client.get(
        "/items/{}".format(item["uuid"]), headers={"accept": "application/json"}
    )
    assert res.status_code == 404
    assert "not found" in str(res.data)


def test_item_update(client, item):
    res = client.put(
        "/items/{}".format(item["uuid"]),
        headers={"accept": "application/json"},
        json=item_attributes(),
    )
    assert res.status_code == 204

    res = client.get(
        "/items/{}".format(item["uuid"]), headers={"accept": "application/json"}
    )
    assert res.status_code == 200
    assert "somename" in str(res.data)


def test_item_update_non_existing(client, item):
    res = client.put(
        "/items/{}".format(UUID_ZERO),
        headers={"accept": "application/json"},
        json=item_attributes(),
    )
    assert res.status_code == 404


def test_collection_item_update(client, item):
    res = client.put(
        "/collections/{}/items/{}".format(item["collection_uuid"], item["uuid"]),
        headers={"accept": "application/json"},
        json=item_attributes(),
    )
    assert res.status_code == 204

    res = client.get(
        "/collections/{}/items/{}".format(item["collection_uuid"], item["uuid"]),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "somename" in str(res.data)


def test_items_update_geojson(client, item):
    geojson = item_attributes_geojson()
    geojson["features"][0]["id"] = item["uuid"]
    res = client.put("/items", headers={"accept": "application/geojson"}, json=geojson)
    assert res.status_code == 201

    res = client.get(
        "/items/{}".format(item["uuid"]), headers={"accept": "application/json"}
    )
    assert res.status_code == 200

    assert "somegeojson" in str(res.data)


def test_collection_update_items_geojson(client, item):
    res = client.put(
        "/collections/{}/items".format(item["collection_uuid"]),
        headers={"accept": "application/geojson"},
        json=item_attributes_geojson(),
    )
    assert res.status_code == 201

    res = client.get(
        "/collections/{}/items".format(item["collection_uuid"]),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "somegeojson" in str(res.data)
    assert "test-item1" in str(res.data)


def test_item_creation_in_non_existent_collection(client):
    import uuid

    res = client.post(
        "/collections/{}/items".format(uuid.uuid4()), json=item_attributes()
    )
    assert res.status_code == 404


def test_api_can_get_item_by_collection_uuid_and_uuid(client, item):
    res = client.get(
        "/collections/{}/items/{}".format(item["collection_uuid"], item["uuid"])
    )

    assert res.status_code == 200
    assert item["properties"]["name"] in str(res.data)


def test_api_error_on_item_not_found(client, collection):
    res = client.get(
        "/collections/{}/items/{}".format(collection["uuid"], collection["uuid"])
    )

    assert res.status_code == 404


@pytest.mark.slow
def test_generate_walking_paths(client, obstacles, sensors, collection):
    res = client.post(
        "/collections/{}/items/ai/generate/walkingpaths?{}={}&{}={}".format(
            collection["uuid"],
            "starting_points_collection_uuid",
            sensors["uuid"],
            "environment_collection_uuid",
            obstacles["uuid"],
        )
    )
    assert res.status_code == 201


@pytest.mark.slow
def test_get_sequence(client, obstacles, sensors, collection):
    res = client.get(
        "/collections/{}/items?property_filter=Cid=6".format(sensors["uuid"])
    )
    assert res.status_code == 200
    print(res.data)
    items_hash = json.loads(res.data.decode("utf-8"))

    res = client.get(
        "/items/{}/ai/sequence?startdate=2020-06-01&enddate=2020-06-07".format(
            items_hash[0]["uuid"]
        )
    )
    assert res.status_code == 200
    assert "predicted" in str(res.data)


# def test_test(collection, session):
#     from app.models import Item
#     Item.set_session(session)
#
#     item = Item.create(geometry=None,
#                        properties={},
#                        collection_uuid=collection['uuid'],
#                        provider_uuid=collection['provider_uuid'])
#     #Item.session.commit()
#     items = Item.find_by_collection_uuid(collection['uuid'],
#                                          {'valid': None, 'offset': 0, 'limit': 10, 'property_filter': None})
#     print(items[0].to_dict())
#
#     #item2 = items[0]
#     #print(item2.provider_uuid)


def test_get_all_items(client):
    res = client.get("/items", headers={"accept": "application/json"})
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.data))
    items = json.loads(res.data.decode("utf-8"))
    assert len(items) > 0


def test_get_all_items_geojson(client):
    res = client.get("/items", headers={"accept": "application/geojson"})
    assert res.status_code == 200
    feature_collection = json.loads(res.data.decode("utf-8"))
    assert len(feature_collection["features"]) > 0


def test_get_all_items_png(client):
    res = client.get("/items", headers={"accept": "image/png"})
    assert res.status_code == 200
    mime = magic.from_buffer(res.data, mime=True)
    assert mime == "image/png"


def test_get_items_by_name_with_collection_uuids(client, collection, collection2):
    res = client.get(
        "/collections/by_name/{}/items?collection_uuids={}".format(
            collection["name"], collection["uuid"]
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.data))
    assert "test-item1" in str(res.data)
    assert "test-item2" not in str(res.data)

    res = client.get(
        "/collections/by_name/{}/items?collection_uuids={}".format(
            collection2["name"], collection2["uuid"]
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.data))
    assert "test-item1" not in str(res.data)
    assert "test-item2" in str(res.data)

    res = client.get(
        "/collections/by_name/{}/items?collection_uuids={},{}".format(
            collection["name"], collection["uuid"], collection2["uuid"]
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.data))
    assert "test-item1" in str(res.data)
    assert "test-item2" in str(res.data)


def test_get_items_by_name_with_invalid_spatial_filter(client, collection, collection2):
    spatial_filter = "NON_EXISTING"
    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}".format(
            collection["name"], spatial_filter
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 400


def test_get_items_by_name_with_invalid_within_distance(
    client, collection, collection2
):
    # Missing spatial_filter.distance.d should make it return 400
    spatial_filter = "within-distance"
    fp = "spatial_filter.distance"
    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}".format(
            collection["name"], spatial_filter, fp + ".x", "0.0", fp + ".y", "0.0"
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 400


def test_get_items_by_name_with_within_distance(client, collection, collection2):
    spatial_filter = "within-distance"
    fp = "spatial_filter.distance"
    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}".format(
            collection["name"],
            spatial_filter,
            fp + ".x",
            "0.0",
            fp + ".y",
            "0.0",
            fp + ".d",
            "1000.0",
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item1" in str(res.data)
    assert "test-item2" not in str(res.data)

    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}".format(
            collection["name"],
            spatial_filter,
            fp + ".x",
            "1.0",
            fp + ".y",
            "1.0",
            fp + ".d",
            "1000.0",
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item1" not in str(res.data)
    assert "test-item2" in str(res.data)


def test_get_items_by_name_with_within_envelope(client, collection, collection2):
    spatial_filter = "within"
    fp = "spatial_filter.envelope"
    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}&{}={}".format(
            collection["name"],
            spatial_filter,
            fp + ".ymin",
            "-0.5",
            fp + ".xmin",
            "-0.5",
            fp + ".ymax",
            "0.5",
            fp + ".xmax",
            "0.5",
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item1" in str(res.data)
    assert "test-item2" not in str(res.data)

    spatial_filter = "within"
    fp = "spatial_filter.envelope"
    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}&{}={}".format(
            collection["name"],
            spatial_filter,
            fp + ".ymin",
            "0.5",
            fp + ".xmin",
            "0.5",
            fp + ".ymax",
            "1.5",
            fp + ".xmax",
            "1.5",
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item1" not in str(res.data)
    assert "test-item2" in str(res.data)


def test_get_items_by_name_with_within_point(client, collection, collection2):
    spatial_filter = "within"
    fp = "spatial_filter.point"
    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}".format(
            collection["name"], spatial_filter, fp + ".y", "0.5", fp + ".x", "0.5"
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" in str(res.data)
    assert "test-item1" not in str(res.data)
    assert "test-item2" not in str(res.data)

    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}".format(
            collection["name"], spatial_filter, fp + ".y", "1.5", fp + ".x", "1.5"
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" not in str(res.data)
    assert "test-item1" not in str(res.data)
    assert "test-item2" not in str(res.data)


def test_get_items_by_name_with_intersect_envelope(client, collection, collection2):
    spatial_filter = "intersect"
    fp = "spatial_filter.envelope"
    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}&{}={}".format(
            collection["name"],
            spatial_filter,
            fp + ".ymin",
            "-0.5",
            fp + ".xmin",
            "-0.5",
            fp + ".ymax",
            "0.5",
            fp + ".xmax",
            "0.5",
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item1" in str(res.data)
    assert "test-item2" not in str(res.data)

    spatial_filter = "within"
    fp = "spatial_filter.envelope"
    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}&{}={}".format(
            collection["name"],
            spatial_filter,
            fp + ".ymin",
            "0.5",
            fp + ".xmin",
            "0.5",
            fp + ".ymax",
            "1.5",
            fp + ".xmax",
            "1.5",
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item1" not in str(res.data)
    assert "test-item2" in str(res.data)


def test_get_items_by_name_with_intersect_point(client, collection, collection2):
    spatial_filter = "intersect"
    fp = "spatial_filter.point"
    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}".format(
            collection["name"], spatial_filter, fp + ".y", "0.5", fp + ".x", "0.5"
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" in str(res.data)
    assert "test-item1" not in str(res.data)
    assert "test-item2" not in str(res.data)

    res = client.get(
        "/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}".format(
            collection["name"], spatial_filter, fp + ".y", "1.5", fp + ".x", "1.5"
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" not in str(res.data)
    assert "test-item1" not in str(res.data)
    assert "test-item2" not in str(res.data)


def test_get_items_by_name_with_property_filter(client, collection, collection2):
    res = client.get(
        "/collections/by_name/{}/items?property_filter=name=test-item1".format(
            collection["name"]
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" not in str(res.data)
    assert "test-item1" in str(res.data)
    assert "test-item2" not in str(res.data)

    res = client.get(
        "/collections/by_name/{}/items?property_filter=name=test-item1,second_prop=test-prop1".format(
            collection["name"]
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" not in str(res.data)
    assert "test-item1" in str(res.data)
    assert "test-item2" not in str(res.data)
