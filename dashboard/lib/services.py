from flask import request, jsonify, Blueprint

from dashboard.constants import normalize_jac_string
from dashboard.db.client import supabase_cli
from dashboard.lib.admin import verify_webhook
from dashboard.lib.hooks import Hooks
from dashboard.lib.notifier import Notifier
from dashboard.lib.order.order import extract_order_keys, get_coordinates, extract_line_items_keys

import json

secure_hooks = Hooks()

services_bp = Blueprint('services', __name__)



@services_bp.route('/check_availability', methods=['POST'])
def check_availability():
    data = request.get_json()

    product_name = data['productName']
    if not 'jac' in product_name:
        return jsonify({"unavailable_dates": [], "product_available": True})
    product_name = normalize_jac_string(product_name)

    location = data['location']
    lat, lon = location["lat"], location["lon"]

    dates = supabase_cli.rpc("get_availability_calendar_within_75days", {
        "in_shipping_lon": lon,
        "in_shipping_lat": lat,
        "in_product": product_name
    }).execute().data

    unavailables_within_two_months = [x['the_day'] for x in dates if not x['remain']]

    return jsonify({"unavailable_dates": unavailables_within_two_months,
                    "product_available": bool(len(dates) == len(unavailables_within_two_months))})

@services_bp.route('/order_creation_webhook', methods=['POST'])
def handle_order_creation_webhook():
    notifier = Notifier()

    secure_hooks.flush()

    data = request.get_data()

    try:
        verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))
    except BaseException as e:
        print(e)

    if secure_hooks.check_request(request):
        order = json.loads(data.decode("utf-8"))
        parsed_order = extract_order_keys(order)
        lat, long = get_coordinates(order)
        parsed_order = {
            **parsed_order,
            "shipping_lat": lat,
            "shipping_lon": long,
        }
        line_items = parsed_order.pop("line_items")
        line_items = extract_line_items_keys(line_items, parsed_order["id"])

        _ = (
            supabase_cli.table("orders")
            .insert(parsed_order)
            .execute()
        )

        _ = (
            supabase_cli.table("line_items")
            .insert(line_items)
            .execute()
        )
        notifier(parsed_order, line_items)

        return 'ok', 200

    else:
        return 'you already sent me this hook!', 404