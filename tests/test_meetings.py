from datetime import datetime, timedelta, timezone

def test_create_meeting(client, auth_headers):
    res_c = client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    club_id = res_c.json()["id"]

    scheduled_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    payload = {
        "scheduledAt": scheduled_at,
        "duration": 60,
        "location": "Online",
        "isVirtual": True
    }
    response = client.post(f"/clubs/{club_id}/meetings", json=payload, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["location"] == "Online"

def test_update_attendance(client, auth_headers):
    res_c = client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    club_id = res_c.json()["id"]

    scheduled_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    res_m = client.post(f"/clubs/{club_id}/meetings", json={"scheduledAt": scheduled_at, "duration": 60}, headers=auth_headers)
    meeting_id = res_m.json()["id"]

    payload = {"status": "attending", "note": "I'll be there"}
    response = client.put(f"/clubs/{club_id}/meetings/{meeting_id}/attendance", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "attending"

    # Check attendeeCount
    res_m = client.get(f"/clubs/{club_id}/meetings/{meeting_id}", headers=auth_headers)
    assert res_m.json()["attendeeCount"] == 1

def test_cancel_meeting(client, auth_headers):
    res_c = client.post("/clubs", json={"name": "Club 1", "description": "Desc 1111111111", "theme": "mystery"}, headers=auth_headers)
    club_id = res_c.json()["id"]
    scheduled_at = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    res_m = client.post(f"/clubs/{club_id}/meetings", json={"scheduledAt": scheduled_at, "duration": 60}, headers=auth_headers)
    meeting_id = res_m.json()["id"]

    response = client.delete(f"/clubs/{club_id}/meetings/{meeting_id}", headers=auth_headers)
    assert response.status_code == 204

    res_m = client.get(f"/clubs/{club_id}/meetings/{meeting_id}", headers=auth_headers)
    assert res_m.json()["status"] == "cancelled"
