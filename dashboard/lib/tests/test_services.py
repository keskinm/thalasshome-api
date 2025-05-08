def test_check_delivery_men_around_point(test_db_client):
    in_shipping_lat = 45.39
    result = test_db_client.call_rpc(
        "check_delivery_men_around_point",
        {"in_shipping_lon": 4.31, "in_shipping_lat": in_shipping_lat},
    )
    assert result

    in_shipping_lat = 91  # inexistant
    result = test_db_client.call_rpc(
        "check_delivery_men_around_point",
        {"in_shipping_lon": 4.31, "in_shipping_lat": in_shipping_lat},
    )
    assert not result


def test_check_availability_jacuzzi(test_db_client, client):
    data = {
        "location": {"lat": 48.8566, "lon": 2.3522},
        "productName": "Jacuzzi 4 places 1 nuit",
    }

    response = client.post("/services/check_availability", json=data)
    assert response.status_code == 200

    assert "rent_duration_day" in response.json
