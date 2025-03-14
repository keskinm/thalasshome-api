import base64
import hashlib
import hmac
import json
import os

import requests
from flask import Blueprint, jsonify, request

from dashboard.constants import normalize_jac_string, parse_rent_duration_jac
from dashboard.db.client import supabase_cli
from dashboard.lib.notifier import Notifier
from dashboard.lib.order.order import (
    extract_line_items_keys,
    extract_order_keys,
    get_coordinates,
)

SHOPIFY_STORE_DOMAIN = "spa-detente.myshopify.com"
SHOPIFY_ADMIN_API_VERSION = "2025-01"
SHOPIFY_ADMIN_API_ACCESS_TOKEN = os.getenv("SHOPIFY_ADMIN_API_ACCESS_TOKEN")
SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_WEBHOOK_SECRET")


class Hooks:
    def __init__(self, elt_limit=20):
        self.elt_limit = elt_limit
        self.gottens = {"orders/create": {}}

    def check_request(self, request):
        topic = request.headers.get("X-Shopify-Topic")
        hook_id = request.headers.get("X-Shopify-Order-Id")

        if hook_id not in self.gottens[topic]:
            self.gottens[topic][hook_id] = 0
            return True
        else:
            self.gottens[topic][hook_id] += 1
            return False

    def flush(self):
        for k, v in self.gottens.items():
            if len(v) == self.elt_limit:
                self.gottens[k].pop(list(v.keys())[0])


def verify_webhook(data, hmac_header):
    digest = hmac.new(
        SHOPIFY_WEBHOOK_SECRET, data.encode("utf-8"), hashlib.sha256
    ).digest()
    computed_hmac = base64.b64encode(digest)
    verified = hmac.compare_digest(computed_hmac, hmac_header.encode("utf-8"))
    return verified


secure_hooks = Hooks()

services_bp = Blueprint("services", __name__)


@services_bp.route("/order_creation_webhook", methods=["POST"])
def handle_order_creation_webhook():
    notifier = Notifier()

    secure_hooks.flush()

    data = request.get_data()

    try:
        verify_webhook(data, request.headers.get("X-Shopify-Hmac-SHA256"))
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
            "shipping_phone": parsed_order["shipping_address"]["phone"],
        }
        line_items = parsed_order.pop("line_items")
        line_items = extract_line_items_keys(line_items, parsed_order["id"])

        _ = supabase_cli.table("orders").insert(parsed_order).execute()

        _ = supabase_cli.table("line_items").insert(line_items).execute()
        notifier(parsed_order, line_items)

        return "ok", 200

    else:
        return "you already sent me this hook!", 404


@services_bp.route("/create-20pct-draft", methods=["POST"])
def create_20pct_draft():
    """
    Reçoit (JSON):
      {
        "customerEmail": "client@example.com",
        "productTitle": "Jacuzzi 4 places",
        "totalFullPrice": "80.00"
      }
    Retourne (JSON):
      {
        "success": true,
        "invoiceUrl": "https://myshop.myshopify.com/12345/pay?key=..."
      }
    """
    data = request.json
    try:
        customer_email = data.get("customerEmail")
        product_title = data.get("productTitle")
        total_str = data.get("totalFullPrice", "0")
        full_price = float(total_str)

        # Compute acount = 20% of total
        deposit_price = round(full_price * 0.20, 2)  # 2 décimales

        # Prepare draft orders API payload
        url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/{SHOPIFY_ADMIN_API_VERSION}/draft_orders.json"
        draft_payload = {
            "draft_order": {
                "line_items": [
                    {
                        "title": f"Acompte 20% pour {product_title}",
                        "quantity": 1,
                        "price": str(deposit_price),
                    }
                ],
                "note": f"Acompte de 20% pour {product_title}. "
                f"Reste {round(full_price * 0.8,2)} € à payer à la livraison.",
                "customer": {"email": customer_email},
                "use_customer_default_address": True,
                # We can add "shipping_line", "taxes_included", etc. if necessary
            }
        }

        headers = {
            "X-Shopify-Access-Token": SHOPIFY_ADMIN_API_ACCESS_TOKEN,
            "Content-Type": "application/json",
        }

        # Create draft order
        resp = requests.post(url, json=draft_payload, headers=headers)
        resp.raise_for_status()  # Raise exception if status HTTP != 200

        draft_order = resp.json()["draft_order"]
        # Lien de paiement : draft_order["invoice_url"]
        invoice_url = draft_order["invoice_url"]

        return jsonify(success=True, invoiceUrl=invoice_url)

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


@services_bp.route("/check_availability", methods=["POST"])
def check_availability():
    data = request.get_json()

    location = data["location"]
    lat, lon = location["lat"], location["lon"]

    product_name = data["productName"]
    if not "jac" in product_name.lower():
        n_delivery_men = (
            supabase_cli.rpc(
                "check_delivery_men_around_point",
                {
                    "in_shipping_lon": lon,
                    "in_shipping_lat": lat,
                },
            )
            .single()
            .execute()
            .data["n_delivery_men"]
        )
        return jsonify(
            {
                "unavailable_dates": [],
                "product_available": bool(n_delivery_men),
                "rent_duration_day": None,
            }
        )
    rent_duration_day = parse_rent_duration_jac(product_name)
    product_name = normalize_jac_string(product_name)

    dates = (
        supabase_cli.rpc(
            "get_availability_calendar_within_75days",
            {
                "in_shipping_lon": lon,
                "in_shipping_lat": lat,
                "in_product": product_name,
            },
        )
        .execute()
        .data
    )

    unavailables_within_two_months = [x["the_day"] for x in dates if not x["remain"]]

    return jsonify(
        {
            "unavailable_dates": unavailables_within_two_months,
            "product_available": bool(
                len(dates) == len(unavailables_within_two_months)
            ),
            "rent_duration_day": rent_duration_day,
        }
    )
