import json

from conftest import UUID_ZERO


def test_acl_creation_provider_item(client, client2, user2, item_private):
    # provider -> item
    res = client2.get("/items/{}".format(item_private["uuid"]))
    assert res.status_code == 404

    res = client.post(
        "/acls",
        json={
            "granted_provider_uuid": user2["provider_uuid"],
            "item_uuid": item_private["uuid"],
            "access": "read",
        },
    )
    assert res.status_code == 201

    res = client2.get("/items/{}".format(item_private["uuid"]))
    assert res.status_code == 200


def test_acl_creation_provider_collection(client, client2, user2, item_private):
    # provider -> collection
    res = client2.get("/items/{}".format(item_private["uuid"]))
    assert res.status_code == 404

    res = client.post(
        "/acls",
        json={
            "granted_provider_uuid": user2["provider_uuid"],
            "collection_uuid": item_private["collection_uuid"],
            "access": "read",
        },
    )
    assert res.status_code == 201

    res = client2.get("/items/{}".format(item_private["uuid"]))
    assert res.status_code == 200


def test_acl_creation_user_item(client, client2, user2, item_private):
    # user -> item
    res = client2.get("/items/{}".format(item_private["uuid"]))
    assert res.status_code == 404

    res = client.post(
        "/acls",
        json={
            "granted_user_uuid": user2["uuid"],
            "item_uuid": item_private["uuid"],
            "access": "read",
        },
    )
    assert res.status_code == 201

    res = client2.get("/items/{}".format(item_private["uuid"]))
    assert res.status_code == 200


def test_acl_creation_user_collection(client, client2, user2, item_private):
    # user -> collection
    res = client2.get("/items/{}".format(item_private["uuid"]))
    assert res.status_code == 404

    res = client.post(
        "/acls",
        json={
            "granted_user_uuid": user2["uuid"],
            "collection_uuid": item_private["collection_uuid"],
            "access": "read",
        },
    )
    assert res.status_code == 201

    res = client2.get("/items/{}".format(item_private["uuid"]))
    assert res.status_code == 200


def test_acl_get_by_uuid(client, client2, user2, item_private):
    res = client.post(
        "/acls",
        json={
            "granted_user_uuid": user2["uuid"],
            "item_uuid": item_private["uuid"],
            "access": "read",
        },
    )
    assert res.status_code == 201
    acl = json.loads(res.data.decode("utf-8"))

    res = client.get("/acls/{}".format(acl["uuid"]))
    assert res.status_code == 200

    res = client2.get("/acls/{}".format(acl["uuid"]))
    assert res.status_code == 200


def test_get_acls(client, client2, user2, item_private):
    res = client.post(
        "/acls",
        json={
            "granted_user_uuid": user2["uuid"],
            "item_uuid": item_private["uuid"],
            "access": "read",
        },
    )
    assert res.status_code == 201
    acl = json.loads(res.data.decode("utf-8"))

    res = client.get("/acls")
    assert res.status_code == 200
    acls = json.loads(res.data.decode("utf-8"))
    assert acls[0]["uuid"] == acl["uuid"]


def test_delete_acl(client, client2, user2, item_private):
    res = client.post(
        "/acls",
        json={
            "granted_user_uuid": user2["uuid"],
            "item_uuid": item_private["uuid"],
            "access": "read",
        },
    )
    assert res.status_code == 201
    acl1 = json.loads(res.data.decode("utf-8"))
    res = client.post(
        "/acls",
        json={
            "granted_user_uuid": user2["uuid"],
            "item_uuid": item_private["uuid"],
            "access": "read",
        },
    )
    assert res.status_code == 201
    acl2 = json.loads(res.data.decode("utf-8"))

    res = client.delete("/acls/{}".format(acl1["uuid"]))
    assert res.status_code == 204

    res = client2.delete("/acls/{}".format(acl2["uuid"]))
    assert res.status_code == 204


def test_invalid_acls(client, user2, item_private):
    res = client.post(
        "/acls",
        json={
            "granted_user_uuid": user2["uuid"],
            "granted_provider_uuid": user2["provider_uuid"],
            "item_uuid": item_private["uuid"],
            "access": "read",
        },
    )
    assert res.status_code == 400

    res = client.post(
        "/acls", json={"item_uuid": item_private["uuid"], "access": "read"}
    )
    assert res.status_code == 400

    res = client.post(
        "/acls",
        json={
            "granted_user_uuid": user2["uuid"],
            "item_uuid": item_private["uuid"],
            "collection_uuid": item_private["collection_uuid"],
            "access": "read",
        },
    )
    assert res.status_code == 400

    res = client.post(
        "/acls",
        json={"granted_user_uuid": user2["uuid"], "item_uuid": item_private["uuid"]},
    )
    assert res.status_code == 400


def test_acl_get_by_uuid_non_existing(client, client2, user2, item_private):
    res = client.get("/acls/{}".format(UUID_ZERO))
    assert res.status_code == 404
