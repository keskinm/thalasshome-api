import base64
import hashlib
import hmac
import random

from flask import Blueprint, jsonify, render_template, request, session

from dashboard.db.client import supabase_cli
from dashboard.lib.hooks import Hooks
from dashboard.lib.order.order import get_address, get_ship

secure_hooks = Hooks()


admin_bp = Blueprint("admin", __name__)


def get_cards():
    all_keys = supabase_cli.table("orders").select("*").execute().data
    res = {}

    for item in all_keys:
        status = item["status"]

        delivery_men_id, delivery_men = item.get("delivery_men_id"), None
        if delivery_men_id:
            delivery_men = (
                supabase_cli.table("users")
                .select("*")
                .eq("id", delivery_men_id)
                .limit(1)
                .single()
                .execute()
                .data
            )

        adr = get_address(item)

        line_items = (
            supabase_cli.table("line_items")
            .select("*")
            .eq("order_id", item["id"])
            .execute()
            .data
        )
        ship, amount = get_ship(line_items)

        res.setdefault(status, [])
        res[status].append(
            {
                "address": adr,
                "def_empl": delivery_men["username"] if delivery_men else "None",
                "rep_empl": "Aucun",
                "shipped": ship,
                "amount": amount,
                "item_id": item["id"],
            }
        )

    return res


@admin_bp.route("/ask_zone", methods=["POST"])
def ask_zone():
    data = request.get_json()
    zone = data.get("zone")
    country = data.get("country")

    cards = get_cards(zone, country)

    return jsonify(cards)


@admin_bp.route("/order/status", methods=["PATCH"])
def patch_order_status():
    data = request.get_json()
    item_id = int(data["item"])
    supabase_cli.table("orders").update({"status": data["category"]}).eq(
        "id", item_id
    ).execute()
    return jsonify({"message": "Order status updated"})


def verify_webhook(data, hmac_header):
    # SECRET = 'hush'
    SECRET = "cc226b71cdbaea95db7f42e1d05503f92282097b4fa6409ce8063b81b8727b48"
    digest = hmac.new(SECRET, data.encode("utf-8"), hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    verified = hmac.compare_digest(computed_hmac, hmac_header.encode("utf-8"))
    return verified


@admin_bp.route("/remove_cards", methods=["POST"])
def on_remove_cards():
    data = request.get_json()
    list_id = data["list_id"]
    print("\n ----ON REMOVE CARDS------ \n")

    response = supabase_cli.table("orders").delete().in_("id", list_id).execute()
    return jsonify(
        {
            "message": f"{response.count or 0} cards removed from list",
            "list_id": list_id,
        }
    )


@admin_bp.route("/index.html")
def admin_index():
    if not session.get("logged_in") or not session.get("is_staff"):
        return "Accès interdit", 403

    res = get_cards()
    employee_names = supabase_cli.table("users").select("username").execute().data
    res = {
        **res,
        **{"employees": list(map(lambda x: x.get("username"), employee_names))},
    }

    return render_template("admin/index.html", **res)
