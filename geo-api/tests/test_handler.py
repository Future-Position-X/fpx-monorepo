def test_health(anon_client):
    res = anon_client.get("/health")
    assert "healthy!" in str(res.data)
