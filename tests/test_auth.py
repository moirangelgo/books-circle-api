def test_register_user(client):
    payload = {
        "email": "new@example.com",
        "password": "password123",
        "username": "newuser",
        "fullName": "New User"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    assert response.json()["user"]["email"] == "new@example.com"
    assert "token" in response.json()

def test_register_duplicate_user(client):
    payload = {
        "email": "dup@example.com",
        "password": "password123",
        "username": "dupuser",
        "fullName": "Dup User"
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409

def test_login_success(client):
    payload = {
        "email": "login@example.com",
        "password": "password123",
        "username": "loginuser",
        "fullName": "Login User"
    }
    client.post("/auth/register", json=payload)

    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "token" in response.json()

def test_login_fail(client):
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrong"
    })
    assert response.status_code == 401
