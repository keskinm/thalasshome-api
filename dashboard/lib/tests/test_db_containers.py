import sqlalchemy


def test_example(test_db_client):
    with test_db_client.test_db_engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT COUNT(*) FROM users;"))
        count = result.scalar()
        assert count >= 4


def test_rpc(test_db_client):
    result = test_db_client.call_rpc(
        "check_delivery_men_around_point",
        {"in_shipping_lon": 4.31, "in_shipping_lat": 45.39},
    )
    assert result


def test_select_order(test_db_client, sample_order_line_item):
    result = test_db_client.select_from_table(
        "orders",
        select_columns="*",
        conditions={"email": "sign.pls.up@gmail.com"},
        limit=1,
        single=True,
    )
    assert result
