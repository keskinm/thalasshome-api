def test_check_delivery_men_around_point(test_db_client):
    result = test_db_client.call_rpc(
        "check_delivery_men_around_point",
        {"in_shipping_lon": 4.31, "in_shipping_lat": 45.39},
    )
    assert result

    result = test_db_client.call_rpc(
        "check_delivery_men_around_point",
        {"in_shipping_lon": 4.31, "in_shipping_lat": 91},  # fancy lat,
    )
    assert not result


def test_check_availability_jacuzzi(test_db_client, client):
    send_data = {
        "location": {"lat": 48.8566, "lon": 2.3522},
        "productName": "Jacuzzi 4 places 1 nuit",
    }

    response = client.post("/services/check_availability", json=send_data)
    assert response.status_code == 200
    data = response.json
    assert "rent_duration_day" in data

    send_data = {
        "location": {"lat": 48.8566, "lon": 181},  # fancy lon
        "productName": "Jacuzzi 4 places 1 nuit",
    }

    response2 = client.post("/services/check_availability", json=send_data)
    data2 = response.json
