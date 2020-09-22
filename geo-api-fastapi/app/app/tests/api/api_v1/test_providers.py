from app.core.config import settings


def provider_attributes():
    return {"name": "somename"}


def test_get_providers(client, provider):
    res = client.get(f'{settings.API_V1_STR}/providers')
    assert res.status_code == 200
    assert "test-provider1" in str(res.content)


def test_get_provider(client, provider):
    res = client.get(f'{settings.API_V1_STR}/providers/{provider["uuid"]}')
    assert res.status_code == 200
    assert "test-provider1" in str(res.content)


def test_update_provider(client, provider):
    res = client.put(
        f'{settings.API_V1_STR}/providers/{provider["uuid"]}', json=provider_attributes()
    )
    assert res.status_code == 204
    assert "" in str(res.content)

    res = client.get(f'{settings.API_V1_STR}/providers/{provider["uuid"]}')
    assert res.status_code == 200
    assert "somename" in str(res.content)