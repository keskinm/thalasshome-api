import base64
import hashlib
import hmac
import json
import logging
import os

import requests
from flask import Blueprint, current_app, jsonify, redirect, request

from dashboard.constants import APP_DIR, normalize_jac_string, parse_rent_duration_jac
from dashboard.db.client import call_rpc, insert_into_table, supabase_cli
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


def verify_webhook(data, hmac_header):
    if hmac_header is None:
        raise ValueError("Missing X-Shopify-Hmac-SHA256 header")
    digest = hmac.new(
        SHOPIFY_WEBHOOK_SECRET.encode("utf-8"), data, hashlib.sha256
    ).digest()
    computed_hmac = base64.b64encode(digest)
    verified = hmac.compare_digest(computed_hmac, hmac_header.encode("utf-8"))
    return verified


services_bp = Blueprint("services", __name__)


@services_bp.route("/order_creation_webhook", methods=["POST"])
def order_creation_webhook():
    notifier = Notifier()

    data = request.get_data()

    provided_header = request.headers.get("X-Shopify-Hmac-SHA256")
    if not verify_webhook(data, provided_header):
        logging.error(
            f"Webhook verification failed. Provided header: {provided_header}"
        )
        raise ValueError("Webhook verification failed. Check logs for details.")

    order = json.loads(data.decode("utf-8"))
    parsed_order, line_items = parse_order(order)

    result = insert_into_table("orders", parsed_order)
    result = insert_into_table("line_items", line_items)

    notifier(parsed_order, line_items)

    return "ok", 200


def parse_order(order: dict):
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
    return parsed_order, line_items


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
        delivery_mens = (
            supabase_cli.rpc(
                "check_delivery_men_around_point",
                {
                    "in_shipping_lon": lon,
                    "in_shipping_lat": lat,
                },
            )
            .execute()
            .data
        )
        return jsonify(
            {
                "unavailable_dates": [],
                "product_available": bool(len(delivery_mens)),
                "rent_duration_day": None,
            }
        )
    rent_duration_day = parse_rent_duration_jac(product_name)
    product_name = normalize_jac_string(product_name)

    dates = call_rpc(
        "get_availability_calendar_within_75days",
        {
            "in_shipping_lon": lon,
            "in_shipping_lat": lat,
            "in_product": product_name,
        },
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


@services_bp.route("/test_order_creation_webhook", methods=["GET"])
def test_order_creation_webhook():
    file_path = APP_DIR / "utils" / "orders" / "samples" / "2025_discounted.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.dumps(json.load(f))

    digest = hmac.new(
        SHOPIFY_WEBHOOK_SECRET.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
    ).digest()
    computed_hmac = base64.b64encode(digest).decode("utf-8")

    with current_app.test_client() as client:
        headers = {"X-Shopify-Hmac-SHA256": computed_hmac}
        response = client.post(
            "/services/order_creation_webhook", data=data, headers=headers
        )
        logging.info(response.status_code, response.data.decode("utf-8"))

    return redirect("/")


@services_bp.route("/test_notification", methods=["GET"])
def test_notification():
    order = (
        supabase_cli.table("orders")
        .select("*")
        .limit(1)
        .eq("email", "sign.pls.up@gmail.com")
        .single()
        .execute()
        .data
    )
    line_items = (
        supabase_cli.table("line_items")
        .select("*")
        .eq("order_id", order["id"])
        .execute()
        .data
    )
    Notifier()(order, line_items, test=True)
    return redirect("/")
