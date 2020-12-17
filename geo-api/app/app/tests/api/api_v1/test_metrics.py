from datetime import datetime

from app.core.config import settings


def metric_attributes():
    return {"ts": "2020-12-02T00:00:00.000", "data": {"somedata": 1}}


def test_metric_creation(client, series):
    res = client.post(
        f'{settings.API_V1_STR}/series/{series["uuid"]}/metrics',
        json=metric_attributes(),
    )
    assert res.status_code == 201
    metric_hash = res.json()
    assert datetime.fromisoformat(metric_attributes()["ts"]) == datetime.fromisoformat(
        metric_hash["ts"]
    )


# def test_api_can_get_all_public_collection(anon_client, collection, collection_private):
#     res = anon_client.get(f"{settings.API_V1_STR}/collections")
#     assert res.status_code == 200
#     assert collection["name"] in str(res.content)
#     assert collection_private["name"] not in str(res.content)
#
#
# def test_api_can_get_private_collection(client, collection, collection_private):
#     res = client.get(f"{settings.API_V1_STR}/collections")
#     assert res.status_code == 200
#     assert collection["name"] in str(res.content)
#     assert collection_private["name"] in str(res.content)
#
#
# def test_api_can_get_collection_by_uuid(client, collection):
#     result = client.get(f'{settings.API_V1_STR}/collections/{collection["uuid"]}')
#     assert result.status_code == 200
#     assert collection["name"] in str(result.content)
#
#
# def test_collection_can_be_edited(client, collection):
#     rv = client.put(
#         f'{settings.API_V1_STR}/collections/{collection["uuid"]}',
#         json={"name": "solo", "is_public": True},
#     )
#     assert rv.status_code == 204
#     results = client.get(f'{settings.API_V1_STR}/collections/{collection["uuid"]}')
#     assert "solo" in str(results.content)
#
#
# def test_empty_collection_deletion(client, collection_empty):
#     res = client.delete(f'{settings.API_V1_STR}/collections/{collection_empty["uuid"]}')
#     assert res.status_code == 204
#     result = client.get(f'{settings.API_V1_STR}/collections/{collection_empty["uuid"]}')
#     assert result.status_code == 404
#
#
# def test_collection_can_be_copied_to_new_collection(
#     client, collection, collection_empty, item
# ):
#     res = client.post(
#         f'{settings.API_V1_STR}/collections/{collection["uuid"]}/copy',
#         json=collection_attributes(),
#     )
#     assert res.status_code == 201
#     collection_hash = res.json()
#
#     result = client.get(
#         f'{settings.API_V1_STR}/collections/{collection_hash["uuid"]}/items'
#     )
#     assert result.status_code == 200
#     assert item["properties"]["name"] in str(result.content)
#     assert str(item["uuid"]) not in str(result.content)
#
#
# def test_collection_can_be_copied_to_other_collection(
#     client, collection, collection_empty, item
# ):
#     res = client.post(
#         f'{settings.API_V1_STR}/collections/{collection["uuid"]}/copy/{collection_empty["uuid"]}',
#         data=None,
#     )
#     assert res.status_code == 201
#     collection_hash = res.json()
#
#     assert str(collection_empty["uuid"]) == collection_hash["uuid"]
#
#     result = client.get(
#         f'{settings.API_V1_STR}/collections/{collection_empty["uuid"]}/items'
#     )
#     assert result.status_code == 200
#     assert item["properties"]["name"] in str(result.content)
#     assert str(item["uuid"]) not in str(result.content)
#
#
# def test_copy_non_existent_collection(client, collection, collection_empty, item):
#     res = client.post(
#         f"{settings.API_V1_STR}/collections/{UUID_ZERO}/copy",
#         json=collection_attributes(),
#     )
#     assert res.status_code == 403
