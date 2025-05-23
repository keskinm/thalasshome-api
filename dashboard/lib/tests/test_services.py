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
    # NO AVAILABILITY WITH FANCY COORDINATES
    send_data = {
        "location": {"lat": 91, "lon": 181},  # fancy lon
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
    long, lat = -2.6898, 48.0595
    # AVAILABLE (1 delivery men should)
    send_data = {
        "location": {"lat": lat, "lon": long},
        "productName": "Jacuzzi 4 places 1 nuit",
    }

    response = client.post("/services/check_availability", json=send_data)
    assert response.status_code == 200
    data = response.json
    assert data["rent_duration_day"] == 1
    assert data["product_available"] is True
    assert len(data["unavailable_dates"]) == 2

    parsed_order, line_items = sample_order_line_item

    test_db_client.update_table(
        "orders",
        {"delivery_men_id": sample_provider["id"], "status": "assigned"},
        conditions={"id": parsed_order["id"]},
    )

    # 2 days are unavailable also
    response = client.post("/services/check_availability", json=send_data)
    assert response.status_code == 200
    data = response.json
    assert data["rent_duration_day"] == 1
    assert data["product_available"] is True
    assert len(data["unavailable_dates"]) == 2

    # Insert a new user_delivery_zone on the same zone

    test_db_client.insert_into_table(
        "user_delivery_zones",
        {
            "user_id": sample_provider["id"] + 1,
            "zone_name": "Bréhan",
            "radius_km": 30,
            "center_geog": f"SRID=4326;POINT({long} {lat})",
        },
    )

    # The previously unavailable dates should be available now (another delivery men is available)
    response = client.post("/services/check_availability", json=send_data)
    assert response.status_code == 200
    data = response.json
    assert data["rent_duration_day"] == 1
    assert data["product_available"] is True
    assert len(data["unavailable_dates"]) == 0
    # Pas besoin de rollback explicite, le fixture s'en charge
