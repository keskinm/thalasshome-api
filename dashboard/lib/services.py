import base64
import hashlib
import hmac
import json
import logging
import os
import urllib.parse

import requests
from flask import Blueprint, current_app, jsonify, redirect, request

from dashboard.constants import APP_DIR, normalize_jac_string, parse_rent_duration_jac
from dashboard.container import container
from dashboard.lib.delivery_men import get_delivery_mens
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
    data = request.get_data()

    provided_header = request.headers.get("X-Shopify-Hmac-SHA256")
    if not verify_webhook(data, provided_header):
        logging.error(
            "Webhook verification failed. Provided header: %s", provided_header
        )
        raise ValueError("Webhook verification failed. Check logs for details.")

    order = json.loads(data.decode("utf-8"))
    logging.info("Received order creation webhook: \n\n\n %s \n\n\n ----------", order)
    parsed_order, line_items = parse_order(order)

    container.get("DB_CLIENT").insert_into_table("orders", parsed_order)
    container.get("DB_CLIENT").insert_into_table("line_items", line_items)

    notify_receive_command(parsed_order, line_items)

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


@services_bp.route("/create-20-draft", methods=["POST"])
def create_20_draft():
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

        # Fixed deposit of 20€
        # deposit_price = 20.00

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
                "note": (
                    f"Acompte de 20% pour {product_title}. "
                    f"Reste {round(full_price - deposit_price, 2)} € à payer à la livraison."
                ),
                "customer": {"email": customer_email},
                "use_customer_default_address": True,
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
        delivery_mens = container.get("DB_CLIENT").call_rpc(
            "check_delivery_men_around_point",
            {
                "in_shipping_lon": lon,
                "in_shipping_lat": lat,
            },
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

    dates = container.get("DB_CLIENT").call_rpc(
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
                len(dates) != len(unavailables_within_two_months)
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
    _base_url = f"http://{urllib.parse.urlparse(request.host_url).netloc}"
    with current_app.test_client() as client:
        headers = {"X-Shopify-Hmac-SHA256": computed_hmac}
        response = client.post(
            f"/{services_bp.name}/order_creation_webhook",
            data=data,
            headers=headers,
            base_url=_base_url,
        )

    return redirect("/")


@services_bp.route("/test_notification", methods=["GET"])
def test_notification():
    order = container.get("DB_CLIENT").select_from_table(
        "orders",
        select_columns="*",
        conditions={"email": "sign.pls.up@gmail.com"},
        limit=1,
        single=True,
    )

    line_items = container.get("DB_CLIENT").select_from_table(
        "line_items", select_columns="*", conditions={"order_id": order["id"]}
    )

    notify_receive_command(order, line_items, test=True)
    return redirect("/")


def notify_receive_command(order, line_items, test=False, flask_address=""):
    deliv_mens = get_delivery_mens(order, test=test)
    logging.info(
        "notified providers: %s for a new order!",
        [(d.get("username"), d.get("email")) for d in deliv_mens],
    )
    tokens = create_tokens(order["id"], deliv_mens)
    notifier = Notifier(flask_address=flask_address)
    notifier.notify_providers(deliv_mens, tokens, order, line_items)


def create_tokens(order_id, delivery_mens: list[dict]) -> list[str]:
    tokens = []
    for delivery_man in delivery_mens:
        tokens.append(f"{str(order_id)}|{delivery_man['username']}")
    return tokens
