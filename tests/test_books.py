def test_propose_book(client, auth_headers):
    # Create a club first
    res = client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    club_id = res.json()["id"]

    payload = {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "totalPages": 310
    }
    response = client.post(f"/clubs/{club_id}/books", json=payload, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["title"] == "The Hobbit"
    assert response.json()["votes"] == 1

def test_vote_for_book(client, auth_headers):
    res_c = client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    club_id = res_c.json()["id"]
    res_b = client.post(f"/clubs/{club_id}/books", json={"title": "Book", "author": "Author"}, headers=auth_headers)
    book_id = res_b.json()["id"]

    # Already voted by proposer, so trying to vote again with same user should fail if I implemented it that way
    response = client.post(f"/clubs/{club_id}/books/{book_id}/votes", headers=auth_headers)
    assert response.status_code == 409

    # Let's try to remove vote
    response = client.delete(f"/clubs/{club_id}/books/{book_id}/votes", headers=auth_headers)
    assert response.status_code == 204

    # Check votes
    res_b = client.get(f"/clubs/{club_id}/books/{book_id}", headers=auth_headers)
    assert res_b.json()["votes"] == 0

def test_reading_progress(client, auth_headers):
    res_c = client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    club_id = res_c.json()["id"]
    res_b = client.post(f"/clubs/{club_id}/books", json={"title": "Book", "author": "Author", "totalPages": 100}, headers=auth_headers)
    book_id = res_b.json()["id"]

    payload = {"currentPage": 50, "status": "reading"}
    response = client.put(f"/clubs/{club_id}/books/{book_id}/progress", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["percentage"] == 50.0

    response = client.get(f"/clubs/{club_id}/books/{book_id}/progress", headers=auth_headers)
    assert response.json()["currentPage"] == 50
