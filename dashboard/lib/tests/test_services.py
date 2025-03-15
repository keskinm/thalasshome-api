from unittest.mock import MagicMock

"""
def test_check_availability_jacuzzi(client, mock_supabase):
    def fake_rpc(fn, params):
        mock_rpc = MagicMock()
        mock_rpc.execute.return_value.data = [{"the_day": "2025-03-01", "remain": 2}]
        return mock_rpc

    original = mock_supabase.rpc
    mock_supabase.rpc.side_effect = fake_rpc

    data = {
        "location": {"lat": 48.8566, "lon": 2.3522},
        "productName": "Jacuzzi 4 places 1 nuit",
    }

    response = client.post("/services/check_availability", json=data)
    assert response.status_code == 200

    assert "rent_duration_day" in response.json
    mock_supabase.rpc = original
"""


def test_check_availability_jacuzzi(client, db_engine):
    data = {
        "location": {"lat": 48.8566, "lon": 2.3522},
        "productName": "Jacuzzi 4 places 1 nuit",
    }

    response = client.post("/services/check_availability", json=data)
    assert response.status_code == 200

    assert "rent_duration_day" in response.json
