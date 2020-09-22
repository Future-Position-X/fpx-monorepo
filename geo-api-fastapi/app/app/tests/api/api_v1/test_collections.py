from app.core.config import settings
from app.tests.conftest import UUID_ZERO


def item_attributes():
    return {"geometry": "POINT(1 1)", "properties": {"name": "somename"}}


def collection_attributes():
    return {"name": "gg", "is_public": True}


def test_collection_creation(client):
    res = client.post(f'{settings.API_V1_STR}/collections', json=collection_attributes())
    assert res.status_code == 201
    assert "gg" in str(res.content)


def test_api_can_get_all_public_collection(anon_client, collection, collection_private):
    res = anon_client.get(f'{settings.API_V1_STR}/collections')
    assert res.status_code == 200
    assert collection["name"] in str(res.content)
    assert collection_private["name"] not in str(res.content)


def test_api_can_get_private_collection(client, collection, collection_private):
    res = client.get(f'{settings.API_V1_STR}/collections')
    assert res.status_code == 200
    assert collection["name"] in str(res.content)
    assert collection_private["name"] in str(res.content)


def test_api_can_get_collection_by_uuid(client, collection):
    result = client.get(f'{settings.API_V1_STR}/collections/{collection["uuid"]}')
    assert result.status_code == 200
    assert collection["name"] in str(result.content)


def test_collection_can_be_edited(client, collection):
    rv = client.put(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}',
        json={"name": "solo", "is_public": True},
    )
    assert rv.status_code == 204
    results = client.get(f'{settings.API_V1_STR}/collections/{collection["uuid"]}')
    assert "solo" in str(results.content)


def test_empty_collection_deletion(client, collection_empty):
    res = client.delete(f'{settings.API_V1_STR}/collections/{collection_empty["uuid"]}')
    assert res.status_code == 204
    result = client.get(f'{settings.API_V1_STR}/collections/{collection_empty["uuid"]}')
    assert result.status_code == 404


def test_collection_can_be_copied_to_new_collection(
    client, collection, collection_empty, item
):
    res = client.post(f'{settings.API_V1_STR}/collections/{collection["uuid"]}/copy')
    assert res.status_code == 201
    collection_hash = res.json()

    result = client.get(f'{settings.API_V1_STR}/collections/{collection_hash["uuid"]}/items')
    assert result.status_code == 200
    assert item["properties"]["name"] in str(result.content)
    assert str(item["uuid"]) not in str(result.content)


def test_collection_can_be_copied_to_other_collection(
    client, collection, collection_empty, item
):
    res = client.post(
        f'{settings.API_V1_STR}/collections/{collection["uuid"]}/copy/{collection_empty["uuid"]}',
        data=None,
    )
    assert res.status_code == 201
    collection_hash = res.json()

    assert str(collection_empty["uuid"]) == collection_hash["uuid"]

    result = client.get(f'{settings.API_V1_STR}/collections/{collection_empty["uuid"]}/items')
    assert result.status_code == 200
    assert item["properties"]["name"] in str(result.content)
    assert str(item["uuid"]) not in str(result.content)


def test_copy_non_existent_collection(client, collection, collection_empty, item):
    res = client.post(f'{settings.API_V1_STR}/collections/{UUID_ZERO}/copy')
    assert res.status_code == 403