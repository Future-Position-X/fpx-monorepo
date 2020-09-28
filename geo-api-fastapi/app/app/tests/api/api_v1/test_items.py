import uuid

import magic
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings


def item_attributes():
    return {"geometry": "POINT(1 1)", "properties": {"name": "somename"}}


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


def test_read_item(client: TestClient, db: Session) -> None:
    response = client.get(f"{settings.API_V1_STR}/items")
    assert response.status_code == 200
    content = response.json()
    assert content is not None
