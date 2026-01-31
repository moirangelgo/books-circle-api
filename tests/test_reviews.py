def test_create_and_delete_review(client, auth_headers):
    res_c = client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    club_id = res_c.json()["id"]
    res_b = client.post(f"/clubs/{club_id}/books", json={"title": "Book", "author": "Author"}, headers=auth_headers)
    book_id = res_b.json()["id"]

    payload = {
        "rating": 5,
        "title": "Amazing book",
        "content": "This book is absolutely amazing and I highly recommend it to everyone " * 2
    }
    response = client.post(f"/clubs/{club_id}/books/{book_id}/reviews", json=payload, headers=auth_headers)
    assert response.status_code == 201
    review_id = response.json()["id"]

    # List reviews
    response = client.get(f"/clubs/{club_id}/books/{book_id}/reviews", headers=auth_headers)
    assert len(response.json()["data"]) == 1

    # Update review
    payload["title"] = "Even more amazing"
    response = client.put(f"/clubs/{club_id}/books/{book_id}/reviews/{review_id}", json=payload, headers=auth_headers)
    assert response.json()["title"] == "Even more amazing"

    # Delete review
    response = client.delete(f"/clubs/{club_id}/books/{book_id}/reviews/{review_id}", headers=auth_headers)
    assert response.status_code == 204
