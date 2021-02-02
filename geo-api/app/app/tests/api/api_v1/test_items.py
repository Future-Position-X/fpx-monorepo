import uuid

import magic
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.conftest import UUID_ZERO


def collection_attributes():
    return {"name": "gg", "is_public": True}


def item_attributes1():
    return {
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        "properties": {"name": "somename"},
    }


def item_attributes():
    return {"geometry": "POINT(1 1)", "properties": {"name": "somename"}}


def item_attributes_empty_geometry():
    return {"geometry": None, "properties": {"name": "somenameempty"}}


def item_attributes_feature():
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [16.9904, 60.6358],
                    [16.9897, 60.6351],
                    [16.9884, 60.6331],
                    [16.9879, 60.6316],
                    [16.9904, 60.6358],
                ]
            ],
        },
        "properties": {"name": "somefeature"},
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
                            [16.9904, 60.6358],
                            [16.9897, 60.6351],
                            [16.9884, 60.6331],
                            [16.9879, 60.6316],
                            [16.9904, 60.6358],
                        ]
                    ],
                },
                "properties": {"name": "somegeojson"},
            }
        ],
    }


def test_get_collection_item_json(client, item):
    res = client.get(
        f'{settings.API_V1_STR}/collections/{item["collection_uuid"]}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    item_hash = res.json()

    assert {
        "uuid": str(item["uuid"]),
        "collection_uuid": str(item["collection_uuid"]),
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        "properties": {"name": "test-item1", "second_prop": "test-prop1"},
    }.items() <= item_hash.items()


def test_get_collection_item_json_404(client, item):
    res = client.get(
        f'{settings.API_V1_STR}/collections/{item["collection_uuid"]}/items/{uuid.uuid4()}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 404
    assert "not found" in str(res.content.lower())


def test_get_collection_item_geojson(client, item):
    res = client.get(
        f'{settings.API_V1_STR}/collections/{item["collection_uuid"]}/items/{item["uuid"]}',
        headers={"accept": "application/geojson"},
    )
    assert res.status_code == 200
    item_hash = res.json()

    assert {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        "properties": {"name": "test-item1", "second_prop": "test-prop1"},
    }.items() <= item_hash.items()


def test_get_collection_item_png(client, item):
    res = client.get(
        f'{settings.API_V1_STR}/collections/{item["collection_uuid"]}/items/{item["uuid"]}?map_id=transparent',
        headers={"accept": "image/png"},
    )
    assert res.status_code == 200
    mime = magic.from_buffer(res.content, mime=True)
    assert mime == "image/png"


@pytest.mark.skip
def test_delete_collection_item(client, item):
    res = client.delete(
        f'{settings.API_V1_STR}/collections/{item["collection_uuid"]}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 204

    res = client.get(
        f'{settings.API_V1_STR}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 404
    assert "Not found" in str(res.content)


def test_delete_collection_items(client, item):
    res = client.delete(
        f'{settings.API_V1_STR}/collections/{item["collection_uuid"]}/items',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 204

    res = client.get(
        f'{settings.API_V1_STR}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 404
    assert "Not found" in str(res.content)


def test_get_item_json(client, item):
    res = client.get(
        f'{settings.API_V1_STR}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    item_hash = res.json()

    assert {
        "uuid": str(item["uuid"]),
        "collection_uuid": str(item["collection_uuid"]),
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        "properties": {"name": "test-item1", "second_prop": "test-prop1"},
    }.items() <= item_hash.items()


def test_get_item_json_404(client, item):
    res = client.get(
        f"{settings.API_V1_STR}/items/{uuid.uuid4()}",
        headers={"accept": "application/json"},
    )
    assert res.status_code == 404
    assert "Not found" in str(res.content)


def test_get_item_geojson(client, item):
    res = client.get(
        f'{settings.API_V1_STR}/items/{item["uuid"]}',
        headers={"accept": "application/geojson"},
    )
    assert res.status_code == 200
    item_hash = res.json()

    assert {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        "properties": {"name": "test-item1", "second_prop": "test-prop1"},
    }.items() <= item_hash.items()


def test_get_item_png(client, item):
    res = client.get(
        f'{settings.API_V1_STR}/items/{item["uuid"]}?map_id=transparent',
        headers={"accept": "image/png"},
    )
    assert res.status_code == 200
    mime = magic.from_buffer(res.content, mime=True)
    assert mime == "image/png"


def test_get_items(client, collection):
    res = client.get(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}/items',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.content))
    assert "test-item1" in str(res.content)
    assert "test-item-empty1" in str(res.content)

    res = client.get(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}/items?valid=true',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.content))
    assert "test-item1" in str(res.content)
    assert "test-item-empty1" not in str(res.content)


def test_get_shared_items(client, user2, client2, collection_private):
    res = client2.get(
        f'{settings.API_V1_STR}/collections/{collection_private["uuid"]}/items',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    items_array = res.json()
    assert len(items_array) == 0

    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_provider_uuid": str(user2["provider_uuid"]),
            "collection_uuid": str(collection_private["uuid"]),
            "access": "read",
        },
        headers={"accept": "application/json"},
    )

    assert res.status_code == 201
    acl = res.json()

    res = client2.get(
        f'{settings.API_V1_STR}/collections/{collection_private["uuid"]}/items',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-private1" in str(res.content)

    res = client.delete(
        f'{settings.API_V1_STR}/acls/{acl["uuid"]}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 204

    res = client2.get(
        f'{settings.API_V1_STR}/collections/{collection_private["uuid"]}/items',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    items_array = res.json()
    assert len(items_array) == 0


def test_get_items_geojson(client, collection):
    res = client.get(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}/items',
        headers={"accept": "application/geojson"},
    )
    assert res.status_code == 200
    assert "FeatureCollection" in str(res.content)
    assert "test-item1" in str(res.content)
    # We can't represent empty geometry in a FeatureCollection
    assert "test-item-empty1" not in str(res.content)


def test_get_items_png(client, collection):
    res = client.get(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}/items?map_id=transparent',
        headers={"accept": "image/png"},
    )
    assert res.status_code == 200
    mime = magic.from_buffer(res.content, mime=True)
    assert mime == "image/png"


def test_get_items_by_name(client, collection):
    res = client.get(
        f'{settings.API_V1_STR}/collections/by_name/{collection["name"]}/items',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.content))
    assert "test-item1" in str(res.content)


def test_get_items_by_name_geojson(client, collection):
    res = client.get(
        f'{settings.API_V1_STR}/collections/by_name/{collection["name"]}/items',
        headers={"accept": "application/geojson"},
    )
    assert res.status_code == 200
    assert "FeatureCollection" in str(res.content)
    assert "test-item1" in str(res.content)


def test_get_items_by_name_png(client, collection):
    res = client.get(
        f'{settings.API_V1_STR}/collections/by_name/{collection["name"]}/items?map_id=transparent',
        headers={"accept": "image/png"},
    )
    assert res.status_code == 200
    mime = magic.from_buffer(res.content, mime=True)
    assert mime == "image/png"


def test_item_creation(client, collection):
    res = client.post(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}/items',
        json=item_attributes(),
        headers={"accept": "application/json"},
    )

    assert res.status_code == 201
    item_hash = res.json()

    res = client.get(
        f'{settings.API_V1_STR}/collections/{item_hash["collection_uuid"]}/items/{item_hash["uuid"]}'
    )
    assert res.status_code == 200
    assert "somename" in str(res.content)


def test_item_creation_geojson(client, collection, item):
    res = client.post(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}/items',
        json=item_attributes_feature(),
        headers={
            "accept": "application/geojson",
            "content-type": "application/geojson",
        },
    )
    print(res.content)
    assert res.status_code == 201

    assert "somefeature" in str(res.content)


def test_item_creation_empty_geom(client, collection):
    res = client.post(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}/items',
        json=item_attributes_empty_geometry(),
    )
    assert res.status_code == 201
    item_hash = res.json()

    res = client.get(
        f'{settings.API_V1_STR}/collections/{item_hash["collection_uuid"]}/items/{item_hash["uuid"]}'
    )

    assert res.status_code == 200
    assert "somenameempty" in str(res.content)


def test_items_creation_geojson_replace(client, collection, item):
    res = client.post(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}/items/replace',
        json=item_attributes_geojson(),
        headers={"accept": "application/json", "content-type": "application/geojson"},
    )
    assert res.status_code == 201
    items = res.json()

    assert len(items) == 1
    assert items[0]["uuid"] != item["uuid"]


def test_items_creation_geojson(client, collection, item):
    res = client.post(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}/items/bulk',
        json=item_attributes_geojson(),
        headers={"accept": "application/json", "content-type": "application/geojson"},
    )
    assert res.status_code == 201
    items = res.json()

    assert len(items) == 1
    assert items[0]["uuid"] != item["uuid"]


def test_item_delete(client, item):
    res = client.delete(
        f'{settings.API_V1_STR}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 204

    res = client.get(
        f'{settings.API_V1_STR}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 404
    assert "Not found" in str(res.content)


def test_item_update(client, item):
    res = client.put(
        f'{settings.API_V1_STR}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
        json=item_attributes(),
    )
    print(res.content)
    assert res.status_code == 204

    res = client.get(
        f'{settings.API_V1_STR}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "somename" in str(res.content)


def test_item_update_non_existing(client, item):
    res = client.put(
        f"{settings.API_V1_STR}/items/{UUID_ZERO}",
        headers={"accept": "application/json"},
        json=item_attributes(),
    )
    assert res.status_code == 404


def test_collection_item_update(client, item):
    res = client.put(
        f'{settings.API_V1_STR}/collections/{item["collection_uuid"]}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
        json=item_attributes(),
    )
    assert res.status_code == 204

    res = client.get(
        f'{settings.API_V1_STR}/collections/{item["collection_uuid"]}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "somename" in str(res.content)


def test_items_update_geojson(client, item):
    geojson = item_attributes_geojson()
    geojson["features"][0]["id"] = str(item["uuid"])
    res = client.put(
        f"{settings.API_V1_STR}/items",
        headers={"accept": "application/geojson"},
        json=geojson,
    )
    assert res.status_code == 204

    res = client.get(
        f'{settings.API_V1_STR}/items/{item["uuid"]}',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200

    assert "somegeojson" in str(res.content)


def test_collection_update_items_geojson(client, item):
    geojson = item_attributes_geojson()
    geojson["features"][0]["id"] = str(item["uuid"])
    res = client.put(
        f'{settings.API_V1_STR}/collections/{item["collection_uuid"]}/items',
        headers={"accept": "application/geojson"},
        json=geojson,
    )
    assert res.status_code == 204

    res = client.get(
        f'{settings.API_V1_STR}/collections/{item["collection_uuid"]}/items',
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "somegeojson" in str(res.content)


def test_item_creation_in_non_existent_collection(client):
    import uuid

    res = client.post(
        f"{settings.API_V1_STR}/collections/{uuid.uuid4()}/items",
        json=item_attributes(),
    )
    assert res.status_code == 404


def test_api_can_get_item_by_collection_uuid_and_uuid(client, item):
    res = client.get(
        f'{settings.API_V1_STR}/collections/{item["collection_uuid"]}/items/{item["uuid"]}'
    )

    assert res.status_code == 200
    assert item["properties"]["name"] in str(res.content)


def test_api_error_on_item_not_found(client, collection):
    res = client.get(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}/items/{collection["uuid"]}'
    )

    assert res.status_code == 404


# @pytest.mark.slow
# def test_generate_walking_paths(client, obstacles, sensors, collection):
#     res = client.post(
#         "/collections/{}/items/ai/generate/walkingpaths?{}={}&{}={}".format(
#             collection["uuid"],
#             "starting_points_collection_uuid",
#             sensors["uuid"],
#             "environment_collection_uuid",
#             obstacles["uuid"],
#         )
#     )
#     assert res.status_code == 201
#
#
# @pytest.mark.slow
# def test_get_sequence(client, obstacles, sensors, collection):
#     res = client.get(
#         "/collections/{}/items?property_filter=Cid=6".format(sensors["uuid"])
#     )
#     assert res.status_code == 200
#     print(res.data)
#     items_hash = json.loads(res.data.decode("utf-8"))
#
#     res = client.get(
#         "/items/{}/ai/sequence?startdate=2020-06-01&enddate=2020-06-07".format(
#             items_hash[0]["uuid"]
#         )
#     )
#     assert res.status_code == 200
#     assert "predicted" in str(res.data)


def test_get_all_items(client):
    res = client.get(
        f"{settings.API_V1_STR}/items", headers={"accept": "application/json"}
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.content))
    items = res.json()
    assert len(items) > 0


def test_get_all_items_geojson(client):
    res = client.get(
        f"{settings.API_V1_STR}/items", headers={"accept": "application/geojson"}
    )
    assert res.status_code == 200
    feature_collection = res.json()
    assert len(feature_collection["features"]) > 0


def test_get_all_items_png(client):
    res = client.get(f"{settings.API_V1_STR}/items", headers={"accept": "image/png"})
    assert res.status_code == 200
    mime = magic.from_buffer(res.content, mime=True)
    assert mime == "image/png"


def test_get_items_by_name_with_collection_uuids(client, collection, collection2):
    res = client.get(
        "{}/collections/by_name/{}/items?collection_uuids={}".format(
            settings.API_V1_STR, collection["name"], collection["uuid"]
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.content))
    assert "test-item1" in str(res.content)
    assert "test-item2" not in str(res.content)

    res = client.get(
        "{}/collections/by_name/{}/items?collection_uuids={}".format(
            settings.API_V1_STR, collection2["name"], collection2["uuid"]
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.content))
    assert "test-item1" not in str(res.content)
    assert "test-item2" in str(res.content)

    res = client.get(
        "{}/collections/by_name/{}/items?collection_uuids={},{}".format(
            settings.API_V1_STR,
            collection["name"],
            collection["uuid"],
            collection2["uuid"],
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert not ("FeatureCollection" in str(res.content))
    assert "test-item1" in str(res.content)
    assert "test-item2" in str(res.content)


def test_get_items_by_name_with_invalid_spatial_filter(client, collection, collection2):
    spatial_filter = "NON_EXISTING"
    res = client.get(
        f'{settings.API_V1_STR}/collections/by_name/{collection["name"]}/items?spatial_filter={spatial_filter}',
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
        "{}/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}".format(
            settings.API_V1_STR,
            collection["name"],
            spatial_filter,
            fp + ".x",
            "0.0",
            fp + ".y",
            "0.0",
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 400


def test_get_items_by_name_with_within_distance(client, collection, collection2):
    spatial_filter = "within-distance"
    fp = "spatial_filter.distance"
    res = client.get(
        "{}/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}".format(
            settings.API_V1_STR,
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
    assert "test-item1" in str(res.content)
    assert "test-item2" not in str(res.content)

    res = client.get(
        "{}/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}".format(
            settings.API_V1_STR,
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
    assert "test-item1" not in str(res.content)
    assert "test-item2" in str(res.content)


def test_get_items_by_name_with_within_envelope(client, collection, collection2):
    spatial_filter = "within"
    fp = "spatial_filter.envelope"
    res = client.get(
        "{}/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}&{}={}".format(
            settings.API_V1_STR,
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
    assert "test-item1" in str(res.content)
    assert "test-item2" not in str(res.content)

    spatial_filter = "within"
    fp = "spatial_filter.envelope"
    res = client.get(
        "{}/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}&{}={}".format(
            settings.API_V1_STR,
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
    assert "test-item1" not in str(res.content)
    assert "test-item2" in str(res.content)


def test_get_items_by_name_with_within_point(client, collection, collection2):
    spatial_filter = "within"
    fp = "spatial_filter.point"
    res = client.get(
        "{}/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}".format(
            settings.API_V1_STR,
            collection["name"],
            spatial_filter,
            fp + ".y",
            "0.5",
            fp + ".x",
            "0.5",
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" in str(res.content)
    assert "test-item1" not in str(res.content)
    assert "test-item2" not in str(res.content)

    res = client.get(
        "{}/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}".format(
            settings.API_V1_STR,
            collection["name"],
            spatial_filter,
            fp + ".y",
            "1.5",
            fp + ".x",
            "1.5",
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" not in str(res.content)
    assert "test-item1" not in str(res.content)
    assert "test-item2" not in str(res.content)


def test_get_items_by_name_with_intersect_envelope(client, collection, collection2):
    spatial_filter = "intersect"
    fp = "spatial_filter.envelope"
    res = client.get(
        "{}/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}&{}={}".format(
            settings.API_V1_STR,
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
    assert "test-item1" in str(res.content)
    assert "test-item2" not in str(res.content)

    spatial_filter = "within"
    fp = "spatial_filter.envelope"
    res = client.get(
        "{}/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}&{}={}&{}={}".format(
            settings.API_V1_STR,
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
    assert "test-item1" not in str(res.content)
    assert "test-item2" in str(res.content)


def test_get_items_by_name_with_intersect_point(client, collection, collection2):
    spatial_filter = "intersect"
    fp = "spatial_filter.point"
    res = client.get(
        "{}/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}".format(
            settings.API_V1_STR,
            collection["name"],
            spatial_filter,
            fp + ".y",
            "0.5",
            fp + ".x",
            "0.5",
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" in str(res.content)
    assert "test-item1" not in str(res.content)
    assert "test-item2" not in str(res.content)

    res = client.get(
        "{}/collections/by_name/{}/items?spatial_filter={}&{}={}&{}={}".format(
            settings.API_V1_STR,
            collection["name"],
            spatial_filter,
            fp + ".y",
            "1.5",
            fp + ".x",
            "1.5",
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" not in str(res.content)
    assert "test-item1" not in str(res.content)
    assert "test-item2" not in str(res.content)


def test_get_items_by_name_with_property_filter(client, collection, collection2):
    res = client.get(
        "{}/collections/by_name/{}/items?property_filter=name=test-item1".format(
            settings.API_V1_STR, collection["name"]
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" not in str(res.content)
    assert "test-item1" in str(res.content)
    assert "test-item2" not in str(res.content)

    res = client.get(
        "{}/collections/by_name/{}/items?property_filter=name=test-item1,second_prop=test-prop1".format(
            settings.API_V1_STR, collection["name"]
        ),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert "test-item-poly1" not in str(res.content)
    assert "test-item1" in str(res.content)
    assert "test-item2" not in str(res.content)


def test_read_item(client: TestClient, db: Session) -> None:
    response = client.get(f"{settings.API_V1_STR}/items")
    assert response.status_code == 200
    content = response.json()
    assert content is not None
