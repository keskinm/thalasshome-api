from flask import request, jsonify, Blueprint

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
    print("CHECK AVAILABILITY", data)

    # --- DO SOME STUFF TO SEE IF THE PRODUCT IS AVAILABLE ---
    return jsonify({"available": True})

@services_bp.route('/order_creation_webhook', methods=['POST'])
def handle_order_creation_webhook():
    print("RECEIVED HOOK")
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
        return 'ok', 200

    else:
        return 'you already sent me this hook!', 404