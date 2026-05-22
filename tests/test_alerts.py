def test_create_alert_requires_auth(client):
    response = client.post(
        "/alerts/",
        json={"coin_name": "bitcoin", "target_price": "50000", "direction": "above"}
    )
    assert response.status_code in (401, 403)


def test_list_alerts_empty(client, auth_headers):
    response = client.get("/alerts/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_create_alert_invalid_coin(client, auth_headers):
    response = client.post(
        "/alerts/",
        json={"coin_name": "fakecoin99999", "target_price": "50000", "direction": "above"},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_create_alert_invalid_direction(client, auth_headers):
    response = client.post(
        "/alerts/",
        json={"coin_name": "bitcoin", "target_price": "50000", "direction": "downwards"},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_create_alert_negative_target_price(client, auth_headers):
    response = client.post(
        "/alerts/",
        json={"coin_name": "bitcoin", "target_price": "-100", "direction": "above"},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_create_alert_zero_target_price(client, auth_headers):
    response = client.post(
        "/alerts/",
        json={"coin_name": "bitcoin", "target_price": "0", "direction": "above"},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_get_alert_not_found(client, auth_headers):
    response = client.get("/alerts/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_alert_not_found(client, auth_headers):
    response = client.delete("/alerts/999", headers=auth_headers)
    assert response.status_code == 404


def test_update_alert_not_found(client, auth_headers):
    response = client.put(
        "/alerts/999",
        json={"target_price": "60000", "direction": "above"},
        headers=auth_headers
    )
    assert response.status_code == 404
