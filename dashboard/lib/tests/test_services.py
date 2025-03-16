def test_check_availability_jacuzzi(test_db_client, client):
    data = {
        "location": {"lat": 48.8566, "lon": 2.3522},
        "productName": "Jacuzzi 4 places 1 nuit",
    }

    response = client.post("/services/check_availability", json=data)
    assert response.status_code == 200

    assert "rent_duration_day" in response.json
