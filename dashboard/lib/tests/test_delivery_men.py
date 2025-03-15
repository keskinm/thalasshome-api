import pytest
from flask import session


def test_get_orders(client, mock_supabase):
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    mock_supabase.table().select().is_().eq().execute.return_value.data = []
    mock_supabase.table().select().eq().in_().execute.return_value.data = []
    mock_supabase.table().select().eq().eq().limit().order().execute.return_value.data = (
        []
    )

    response = client.get("/delivery_men/orders")
    assert response.status_code == 200
    assert response.json == {"available": [], "ongoing": [], "completed": []}


def test_complete_order_success(client, mock_supabase):
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    mock_supabase.table().update().match().execute.return_value.data = [{"id": 1}]

    response = client.post("/delivery_men/orders/1/complete")
    assert response.status_code == 200
