from flask import Blueprint, jsonify, request

from dashboard.container import container
from dashboard.lib.order.order import get_address, get_ship

SUPABASE_CLI = container.get("SUPABASE_CLI")
admin_bp = Blueprint("admin", __name__)


def get_cards():
    all_keys = SUPABASE_CLI.table("orders").select("*").execute().data
    res = {}

    for item in all_keys:
        status = item["status"]

        delivery_men_id, delivery_men = item.get("delivery_men_id"), None
        if delivery_men_id:
            delivery_men = (
                SUPABASE_CLI.table("users")
                .select("*")
                .eq("id", delivery_men_id)
                .limit(1)
                .single()
                .execute()
                .data
            )

        adr = get_address(item)

        line_items = (
            SUPABASE_CLI.table("line_items")
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
    SUPABASE_CLI.table("orders").update({"status": data["category"]}).eq(
        "id", item_id
    ).execute()
    return jsonify({"message": "Order status updated"})


@admin_bp.route("/order", methods=["DELETE"])
def delete_order():
    data = request.get_json()
    item_id = int(data["item"])

    response = SUPABASE_CLI.table("orders").delete().eq("id", item_id).execute()
    return jsonify(
        {
            "message": f"{response.count or 0} cards removed from list",
            "list_id": item_id,
        }
    )


@admin_bp.route("/canceled_orders", methods=["DELETE"])
def delete_canceled_orders():
    data = request.get_json()
    item_ids = data["items"]

    response = SUPABASE_CLI.table("orders").delete().in_("id", item_ids).execute()
    return jsonify(
        {
            "message": f"{response.count or 0} cards removed from list",
            "list_ids": item_ids,
        }
    )
