from dashboard.db.client import supabase_cli
from dashboard.lib.admin import check_zone
from dashboard.lib.order.order import extract_order_keys, get_coordinates, extract_line_items_keys, get_address, \
    deprecated_get_ship, get_ship

import json


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
    # parsed_order = OrderSchema(**parsed_order)
    # parsed_order = parsed_order.dict()

    # line_items = ...
    # -------------------------------


    response = (
        supabase_cli.table("orders")
        .insert(parsed_order)
        .execute()
    )

    response = (
        supabase_cli.table("line_items")
        .insert(line_items)
        .execute()
    )


def new_get_cards(query_zone=None, query_country=None):
    all_keys = supabase_cli.table("orders").select("*").execute().data
    res = {}

    for item in all_keys:
        zipcode = item['shipping_address']['zip'] if 'shipping_address' in item else None
        if check_zone(query_zone, query_country, zipcode):
            continue

        status = item['status']

        delivery_men_id, delivery_men = item.get("delivery_men_id"), None
        if delivery_men_id:
            delivery_men = (supabase_cli.
                            table("users").
                            select("*").
                            eq("id", delivery_men_id).
                            limit(1).
                            single().execute().data)


        adr = get_address(item)

        line_items = (supabase_cli.table("line_items").
                      select("*").
                      eq("order_id", item["id"]).
                      execute().data)
        ship, amount = get_ship(line_items)

        res.setdefault(status, [])
        res[status].append({
            'address': adr,
            'def_empl': delivery_men['username'] if delivery_men else "None",
            'rep_empl': 'Aucun',
            'shipped': ship,
            'amount': amount,
            'item_id': item["id"],
        })

    return res
