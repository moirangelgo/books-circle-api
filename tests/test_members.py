def test_join_and_leave_club(client, auth_headers):
    # User 1 creates club
    res_c = client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    club_id = res_c.json()["id"]

    # Register user 2
    user2 = {"email": "user2@example.com", "password": "password123", "username": "user2", "fullName": "User Two"}
    client.post("/auth/register", json=user2)
    res_l = client.post("/auth/login", json={"email": "user2@example.com", "password": "password123"})
    token2 = res_l.json()["token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 2 joins
    response = client.post(f"/clubs/{club_id}/members", headers=headers2)
    assert response.status_code == 201

    # Check members
    res_m = client.get(f"/clubs/{club_id}/members", headers=auth_headers)
    assert len(res_m.json()["data"]) == 2

    # User 2 leaves
    user2_id = res_l.json()["user"]["id"]
    response = client.delete(f"/clubs/{club_id}/members/{user2_id}", headers=headers2)
    assert response.status_code == 204

    # Check members
    res_m = client.get(f"/clubs/{club_id}/members", headers=auth_headers)
    assert len(res_m.json()["data"]) == 1
