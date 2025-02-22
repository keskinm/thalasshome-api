from google.cloud import datastore
from flask import request, jsonify, Blueprint

from dashboard.lib.admin import verify_webhook
from dashboard.lib.hooks import Hooks
from dashboard.lib.notifier import Notifier
from dashboard.lib.order import OrderParser

import json

secure_hooks = Hooks()

services_bp = Blueprint('services', __name__)


client = datastore.Client()


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

    handler = OrderParser()

    if secure_hooks.check_request(request):
        order = handler.parse_data(json.loads(data.decode("utf-8")))

        name = order['id']
        key = client.key("orders", name)
        entity = datastore.Entity(key=key)
        # @todo how to avoid this stupid thing
        for k, v in order.items():
            entity[k] = v
        client.put(entity)

        notifier(order)

        return 'ok', 200

    else:
        return 'you already sent me this hook!', 404