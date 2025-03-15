import json

import pytest


def test_check_availability_non_jacuzzi(client, mock_supabase):
    data = {"location": {"lat": 48.8566, "lon": 2.3522}, "productName": "other_product"}

    mock_supabase.rpc().execute.return_value.data = [{"id": 1}]

    response = client.post("/services/check_availability", json=data)
    assert response.status_code == 200
    assert response.json["product_available"] == True
    assert response.json["unavailable_dates"] == []


def test_check_availability_jacuzzi(client, mock_supabase):
    data = {
        "location": {"lat": 48.8566, "lon": 2.3522},
        "productName": "Jacuzzi 4 places 1 nuit",
    }

    mock_supabase.rpc().execute.return_value.data = [
        {"the_day": "2025-03-01", "remain": 2}
    ]

    response = client.post("/services/check_availability", json=data)
    assert response.status_code == 200
    assert "rent_duration_day" in response.json
