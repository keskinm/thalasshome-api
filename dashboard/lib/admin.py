from flask import Blueprint, jsonify, render_template, request, session

from dashboard.container import container
from dashboard.lib.order.order import get_address, get_ship

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
def admin_index():
    if not session.get("logged_in") or not session.get("is_staff"):
        return "Accès interdit", 403

    return render_template("admin.html", **get_cards())


def get_cards():
    all_keys = container.get("DB_CLIENT").select_from_table(
        "orders", select_columns="*"
    )
    res = {}

    for item in all_keys:
        status = item["status"]

        delivery_men_id, delivery_men = item.get("delivery_men_id"), None
        if delivery_men_id:
            delivery_men = container.get("DB_CLIENT").select_from_table(
                "users",
                select_columns="*",
                conditions={"id": delivery_men_id},
                limit=1,
                single=True,
            )

        adr = get_address(item)

        line_items = container.get("DB_CLIENT").select_from_table(
            "line_items", select_columns="*", conditions={"order_id": item["id"]}
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
    container.get("DB_CLIENT").update_table(
        "orders", {"status": data["category"]}, conditions={"id": item_id}
    )
    return jsonify({"message": "Order status updated"})


@admin_bp.route("/order", methods=["DELETE"])
def delete_order():
    data = request.get_json()
    item_id = int(data["item"])

    container.get("DB_CLIENT").delete_from_table("orders", conditions={"id": item_id})
    return jsonify(
        {
            "message": "Commande supprimée",
            "list_id": item_id,
        }
    )


@admin_bp.route("/canceled_orders", methods=["DELETE"])
def delete_canceled_orders():
    data = request.get_json()
    item_ids = data["items"]

    container.get("DB_CLIENT").delete_from_table("orders", conditions={"id": item_ids})
    return jsonify(
        {
            "message": "Commandes supprimées",
            "list_ids": item_ids,
        }
    )
