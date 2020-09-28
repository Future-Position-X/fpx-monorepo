from app.main import settings
from app.tests.conftest import UUID_ZERO


def test_acl_creation_provider_item(client, client2, user2, item_private):
    # provider -> item
    res = client2.get(f'{settings.API_V1_STR}/items/{item_private["uuid"]}')
    assert res.status_code == 404

    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_provider_uuid": str(user2["provider_uuid"]),
            "item_uuid": str(item_private["uuid"]),
            "access": "read",
        },
    )
    assert res.status_code == 201

    res = client2.get(f'{settings.API_V1_STR}/items/{item_private["uuid"]}')
    assert res.status_code == 200


def test_acl_creation_provider_collection(client, client2, user2, item_private):
    # provider -> collection
    res = client2.get(f'{settings.API_V1_STR}/items/{item_private["uuid"]}')
    assert res.status_code == 404

    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_provider_uuid": str(user2["provider_uuid"]),
            "collection_uuid": str(item_private["collection_uuid"]),
            "access": "read",
        },
    )
    assert res.status_code == 201

    res = client2.get(f'{settings.API_V1_STR}/items/{item_private["uuid"]}')
    assert res.status_code == 200


def test_acl_creation_user_item(client, client2, user2, item_private):
    # user -> item
    res = client2.get(f'{settings.API_V1_STR}/items/{item_private["uuid"]}')
    assert res.status_code == 404

    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_user_uuid": str(user2["uuid"]),
            "item_uuid": str(item_private["uuid"]),
            "access": "read",
        },
    )
    assert res.status_code == 201

    res = client2.get(f'{settings.API_V1_STR}/items/{item_private["uuid"]}')
    assert res.status_code == 200


def test_acl_creation_user_collection(client, client2, user2, item_private):
    # user -> collection
    res = client2.get(f'{settings.API_V1_STR}/items/{item_private["uuid"]}')
    assert res.status_code == 404

    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_user_uuid": str(user2["uuid"]),
            "collection_uuid": str(item_private["collection_uuid"]),
            "access": "read",
        },
    )
    assert res.status_code == 201

    res = client2.get(f'{settings.API_V1_STR}/items/{item_private["uuid"]}')
    assert res.status_code == 200


def test_acl_get_by_uuid(client, client2, user2, item_private):
    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_user_uuid": str(user2["uuid"]),
            "item_uuid": str(item_private["uuid"]),
            "access": "read",
        },
    )
    assert res.status_code == 201
    acl = res.json()

    res = client.get(f'{settings.API_V1_STR}/acls/{acl["uuid"]}')
    assert res.status_code == 200

    res = client2.get(f'{settings.API_V1_STR}/acls/{acl["uuid"]}')
    assert res.status_code == 200


def test_get_acls(client, client2, user2, item_private):
    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_user_uuid": str(user2["uuid"]),
            "item_uuid": str(item_private["uuid"]),
            "access": "read",
        },
    )
    assert res.status_code == 201
    acl = res.json()

    res = client.get(f"{settings.API_V1_STR}/acls")
    assert res.status_code == 200
    acls = res.json()
    assert acls[0]["uuid"] == acl["uuid"]


def test_delete_acl(client, client2, user2, item_private):
    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_user_uuid": str(user2["uuid"]),
            "item_uuid": str(item_private["uuid"]),
            "access": "read",
        },
    )
    assert res.status_code == 201
    acl1 = res.json()
    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_user_uuid": str(user2["uuid"]),
            "item_uuid": str(item_private["uuid"]),
            "access": "read",
        },
    )
    assert res.status_code == 201
    acl2 = res.json()

    res = client.delete(f'{settings.API_V1_STR}/acls/{acl1["uuid"]}')
    assert res.status_code == 204

    res = client2.delete(f'{settings.API_V1_STR}/acls/{acl2["uuid"]}')
    assert res.status_code == 204


def test_invalid_acls(client, user2, item_private):
    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_user_uuid": str(user2["uuid"]),
            "granted_provider_uuid": str(user2["provider_uuid"]),
            "item_uuid": str(item_private["uuid"]),
            "access": "read",
        },
    )
    assert res.status_code == 400

    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={"item_uuid": str(item_private["uuid"]), "access": "read"},
    )
    assert res.status_code == 400

    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_user_uuid": str(user2["uuid"]),
            "item_uuid": str(item_private["uuid"]),
            "collection_uuid": str(item_private["collection_uuid"]),
            "access": "read",
        },
    )
    assert res.status_code == 400

    res = client.post(
        f"{settings.API_V1_STR}/acls",
        json={
            "granted_user_uuid": str(user2["uuid"]),
            "item_uuid": str(item_private["uuid"]),
        },
    )
    assert res.status_code == 400


def test_acl_get_by_uuid_non_existing(client, client2, user2, item_private):
    res = client.get(f"{settings.API_V1_STR}/acls/{UUID_ZERO}")
    assert res.status_code == 404
