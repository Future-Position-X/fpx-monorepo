def provider_attributes():
    return {"name": "somename"}


def test_get_providers(client, provider):
    res = client.get("/providers")
    assert res.status_code == 200
    assert "test-provider" in str(res.data)


def test_get_provider(client, provider):
    res = client.get("/providers/{}".format(provider["uuid"]))
    assert res.status_code == 200
    assert "test-provider" in str(res.data)


def test_update_provider(client, provider):
    res = client.put(
        "/providers/{}".format(provider["uuid"]), json=provider_attributes()
    )
    assert res.status_code == 204
    assert "" in str(res.data)

    res = client.get("/providers/{}".format(provider["uuid"]))
    assert res.status_code == 200
    assert "somename" in str(res.data)
