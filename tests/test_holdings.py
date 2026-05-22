import pytest


@pytest.fixture
def portfolio(client, auth_headers):
    # Create a portfolio for use in holding tests
    response = client.post(
        "/portfolios/",
        json={"name": "Test Portfolio"},
        headers=auth_headers
    )
    return response.json()


def test_create_holding_requires_auth(client, portfolio):
    response = client.post(
        f"/portfolios/{portfolio['id']}/holdings/",
        json={"coin_name": "bitcoin", "amount": "1.0", "buy_price": "40000"}
    )
    assert response.status_code in (401, 403)


def test_list_holdings_empty(client, auth_headers, portfolio):
    response = client.get(
        f"/portfolios/{portfolio['id']}/holdings/",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json() == []


def test_create_holding_invalid_coin(client, auth_headers, portfolio):
    response = client.post(
        f"/portfolios/{portfolio['id']}/holdings/",
        json={"coin_name": "fakecoin99999", "amount": "1.0", "buy_price": "40000"},
        headers=auth_headers
    )
    assert response.status_code == 400


def test_create_holding_invalid_amount(client, auth_headers, portfolio):
    response = client.post(
        f"/portfolios/{portfolio['id']}/holdings/",
        json={"coin_name": "bitcoin", "amount": "0", "buy_price": "40000"},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_create_holding_negative_amount(client, auth_headers, portfolio):
    response = client.post(
        f"/portfolios/{portfolio['id']}/holdings/",
        json={"coin_name": "bitcoin", "amount": "-1.0", "buy_price": "40000"},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_create_holding_negative_buy_price(client, auth_headers, portfolio):
    response = client.post(
        f"/portfolios/{portfolio['id']}/holdings/",
        json={"coin_name": "bitcoin", "amount": "1.0", "buy_price": "-100"},
        headers=auth_headers
    )
    assert response.status_code == 422


def test_get_holding_not_found(client, auth_headers, portfolio):
    response = client.get(
        f"/portfolios/{portfolio['id']}/holdings/999",
        headers=auth_headers
    )
    assert response.status_code == 404


def test_holding_not_found_wrong_portfolio(client, auth_headers, portfolio):
    response = client.get(
        f"/portfolios/999/holdings/1",
        headers=auth_headers
    )
    assert response.status_code == 404
