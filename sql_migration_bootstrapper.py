from dashboard.db.client import supabase_cli
from dashboard.lib.order.order import extract_order_keys, get_coordinates, extract_line_items_keys

import json

from dashboard.lib.order.schemas import OrderSchema


def new_handle_order_creation_webhook():
    with open("./dashboard/utils/orders/samples/2025.json") as fp:
        order = json.load(fp)
    parsed_order = extract_order_keys(order)
    lat, long = get_coordinates(order)
    parsed_order = {
        **parsed_order,
        "shipping_lat": lat,
        "shipping_lon": long,
    }
    line_items = parsed_order.pop("line_items")
    line_items = extract_line_items_keys(line_items, parsed_order["id"])

    # ----- verification steps -----
    parsed_order = OrderSchema(**parsed_order)
    parsed_order = parsed_order.dict()

    # line_items = ...
    # -------------------------------


    response = (
        supabase_cli.table("orders")
        .insert(parsed_order)
        .execute()
    )

    response = (
        supabase_cli.table("line_items")
        .insert(parsed_order["line_items"])
        .execute()
    )

    breakpoint()
    parsed_order

new_handle_order_creation_webhook()
