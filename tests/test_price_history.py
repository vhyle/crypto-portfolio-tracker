def test_get_history_requires_auth(client):
    response = client.get("/history/bitcoin")
    assert response.status_code in (401, 403)


def test_get_history_empty(client, auth_headers):
    response = client.get("/history/bitcoin", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_history_range_requires_auth(client):
    response = client.get("/history/bitcoin/range")
    assert response.status_code in (401, 403)


def test_get_history_range_default(client, auth_headers):
    response = client.get("/history/bitcoin/range", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_history_range_custom_days(client, auth_headers):
    response = client.get("/history/bitcoin/range?days=30", headers=auth_headers)
    assert response.status_code == 200


def test_get_history_range_invalid_days_zero(client, auth_headers):
    response = client.get("/history/bitcoin/range?days=0", headers=auth_headers)
    assert response.status_code == 422


def test_get_history_range_invalid_days_too_many(client, auth_headers):
    response = client.get("/history/bitcoin/range?days=999", headers=auth_headers)
    assert response.status_code == 422
