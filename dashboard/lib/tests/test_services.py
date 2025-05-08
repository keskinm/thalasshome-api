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


def test_check_no_availability_jacuzzi(test_db_client, client):
    # NO AVAILABILITY WITH FANCY LONGITUDE
    send_data = {
        "location": {"lat": 48.8566, "lon": 181},  # fancy lon
        "productName": "Jacuzzi 4 places 1 nuit",
    }

    response = client.post("/services/check_availability", json=send_data)
    data = response.json
    assert data["rent_duration_day"] == 1
    assert data["product_available"] is False
    assert len(data["unavailable_dates"]) > 50


def test_check_availability_jacuzzi(
    test_db_client, client, sample_order_line_item, sample_provider
):
    # 1 AVAILABLITY
    send_data = {
        "location": {"lat": 48.8566, "lon": 2.3522},
        "productName": "Jacuzzi 4 places 1 nuit",
    }

    response = client.post("/services/check_availability", json=send_data)
    assert response.status_code == 200
    data = response.json
    assert data["rent_duration_day"] == 1
    assert data["product_available"] is True
    assert data["unavailable_dates"] == []

    parsed_order, _ = sample_order_line_item

    # MAKE THE DELIVERY MEN UNAVAILABLE
    test_db_client.update_table(
        "orders",
        {"delivery_men_id": sample_provider["id"], "status": "assigned"},
        conditions={"id": parsed_order["id"]},
    )

    send_data = {
        "location": {"lat": 48.8566, "lon": 2.3522},
        "productName": "Jacuzzi 4 places 1 nuit",
    }

    # NO AVAILABILITY SHOULD BE RETURNED
    response = client.post("/services/check_availability", json=send_data)
    assert response.status_code == 200
    data = response.json
    data
