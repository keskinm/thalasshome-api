from dashboard.db.client import select_from_table
from dashboard.db.client_wrapper import DB_CLIENT


def test_example(db_engine):
    with db_engine.connect() as conn:
        result = conn.execute("SELECT COUNT(*) FROM users;")
        count = result.scalar()
        assert count >= 4


def test_rpc(db_engine):
    result = DB_CLIENT.call_rpc(
        "check_delivery_men_around_point",
        {"in_shipping_lon": 4.31, "in_shipping_lat": 45.39},
    )
    assert result is not None


def test_select_order(db_engine, insert_random_order_with_line_item_sample):
    result = select_from_table(
        "orders",
        select_columns="*",
        conditions={"email": "sign.pls.up@gmail.com"},
        limit=1,
        single=True,
        db_engine=db_engine,
    )
    assert result is not None
