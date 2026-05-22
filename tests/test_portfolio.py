def test_create_portfolio(client, auth_headers):
    response = client.post(
        "/portfolios/",
        json={"name": "My Portfolio"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "My Portfolio"


def test_create_portfolio_requires_auth(client):
    response = client.post("/portfolios/", json={"name": "Saving Portfolio"})
    assert response.status_code in (401, 403)


def test_create_duplicate_portfolio_name(client, auth_headers):
    client.post("/portfolios/", json={"name": "Same Name"}, headers=auth_headers)
    response = client.post(
        "/portfolios/",
        json={"name": "Same Name"},
        headers=auth_headers
    )
    assert response.status_code == 409


def test_list_portfolios_empty(client, auth_headers):
    response = client.get("/portfolios/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_portfolios_returns_user_portfolios(client, auth_headers):
    client.post("/portfolios/", json={"name": "Portfolio 1"}, headers=auth_headers)
    client.post("/portfolios/", json={"name": "Portfolio 2"}, headers=auth_headers)

    response = client.get("/portfolios/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_portfolio_not_found(client, auth_headers):
    response = client.get("/portfolios/999", headers=auth_headers)
    assert response.status_code == 404


def test_update_portfolio(client, auth_headers):
    create_response = client.post(
        "/portfolios/",
        json={"name": "Original"},
        headers=auth_headers
    )
    portfolio_id = create_response.json()["id"]

    response = client.put(
        f"/portfolios/{portfolio_id}",
        json={"name": "Updated"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"


def test_delete_portfolio(client, auth_headers):
    create_response = client.post(
        "/portfolios/",
        json={"name": "ToDelete"},
        headers=auth_headers
    )
    portfolio_id = create_response.json()["id"]

    response = client.delete(f"/portfolios/{portfolio_id}", headers=auth_headers)
    assert response.status_code == 204

    # Deleting invalid portfolio
    get_response = client.get(f"/portfolios/{portfolio_id}", headers=auth_headers)
    assert get_response.status_code == 404
