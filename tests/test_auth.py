def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"


def test_register_duplicate_username(client):
    client.post("/auth/register", json={
        "username": "duplicate",
        "password": "password123"
    })
    response = client.post("/auth/register", json={
        "username": "duplicate",
        "password": "password123"
    })
    assert response.status_code == 409


def test_register_short_username(client):
    response = client.post("/auth/register", json={
        "username": "ab",
        "password": "password123"
    })
    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post("/auth/register", json={
        "username": "validuser",
        "password": "short"
    })
    assert response.status_code == 422


def test_login_success(client):
    client.post("/auth/register", json={
        "username": "loginuser",
        "password": "password123"
    })
    response = client.post("/auth/login", json={
        "username": "loginuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "username": "loginuser",
        "password": "password123"
    })
    response = client.post("/auth/login", json={
        "username": "loginuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={
        "username": "doesnotexist",
        "password": "password123"
    })
    assert response.status_code == 401
