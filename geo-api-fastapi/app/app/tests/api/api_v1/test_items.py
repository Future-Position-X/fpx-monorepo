from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.item import create_random_item
import json




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


def test_read_item(
    client: TestClient, db: Session
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/items",
    )
    assert response.status_code == 200
    content = response.json()
    assert content is not None
    # assert content["title"] == item.title
    # assert content["description"] == item.description
    # assert content["id"] == item.id
    # assert content["owner_id"] == item.owner_id

# def test_create_item(
#     client: TestClient, superuser_token_headers: dict, db: Session
# ) -> None:
#     data = {"title": "Foo", "description": "Fighters"}
#     response = client.post(
#         f"{settings.API_V1_STR}/items/", headers=superuser_token_headers, json=data,
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert content["title"] == data["title"]
#     assert content["description"] == data["description"]
#     assert "id" in content
#     assert "owner_id" in content
#
#
# def test_read_item(
#     client: TestClient, superuser_token_headers: dict, db: Session
# ) -> None:
#     item = create_random_item(db)
#     response = client.get(
#         f"{settings.API_V1_STR}/items/{item.id}", headers=superuser_token_headers,
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert content["title"] == item.title
#     assert content["description"] == item.description
#     assert content["id"] == item.id
#     assert content["owner_id"] == item.owner_id
