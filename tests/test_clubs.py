def test_create_club(client, auth_headers):
    payload = {
        "name": "My New Club",
        "description": "A very cool club for testing",
        "theme": "fantasy",
        "isPrivate": False
    }
    response = client.post("/clubs", json=payload, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "My New Club"
    assert response.json()["memberCount"] == 1

def test_list_clubs(client, auth_headers):
    client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    client.post("/clubs", json={"name": "Club 2", "description": "Desc 2222222222", "theme": "fantasy"}, headers=auth_headers)

    response = client.get("/clubs", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2

def test_get_club(client, auth_headers):
    res = client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    club_id = res.json()["id"]

    response = client.get(f"/clubs/{club_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Club 1"

def test_update_club(client, auth_headers):
    res = client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    club_id = res.json()["id"]

    payload = {"name": "Updated Club", "description": "New description here", "theme": "sci-fi"}
    response = client.put(f"/clubs/{club_id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Club"

def test_delete_club(client, auth_headers):
    res = client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    club_id = res.json()["id"]

    response = client.delete(f"/clubs/{club_id}", headers=auth_headers)
    assert response.status_code == 204

    response = client.get(f"/clubs/{club_id}", headers=auth_headers)
    assert response.status_code == 404

def test_list_clubs_pagination_and_filter(client, auth_headers):
    for i in range(5):
        client.post("/clubs", json={"name": f"Club {i}", "description": "Description text", "theme": "fantasy" if i % 2 == 0 else "mystery"}, headers=auth_headers)

    # Filter by theme
    response = client.get("/clubs?theme=fantasy", headers=auth_headers)
    assert response.json()["meta"]["total"] == 3

    # Pagination
    response = client.get("/clubs?limit=2&offset=1", headers=auth_headers)
    assert len(response.json()["data"]) == 2
    assert response.json()["meta"]["hasMore"] is True
