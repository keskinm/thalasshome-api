from flask import request, session, Blueprint, jsonify

from dashboard.constants import JACUZZI6P, JACUZZI4P
from dashboard.db.client import supabase_cli
from dashboard.lib.order.order import get_address, get_ship

delivery_men_bp = Blueprint('delivery_men', __name__)


@delivery_men_bp.route('/delivery_men/orders', methods=['GET'])
def get_orders():
    user_id = session["user_id"]

    available_orders = supabase_cli.table("orders").select("*").is_("delivery_men_id", None).execute().data
    ongoing_orders = supabase_cli.table("orders").select("*").eq("delivery_men_id", user_id).execute().data

    def process_orders(orders):
        results = []
        for order in orders:
            line_items = (supabase_cli.table("line_items").
                          select("*").
                          eq("order_id", order["id"]).
                          execute().data)
            ship, amount = get_ship(line_items)
            results.append({
                "address": get_address(order),
                "phone": order["phone"],
                "ship": ship,
                "amount": amount
            })
        return results

    return jsonify({
        "available": process_orders(available_orders),
        "ongoing": process_orders(ongoing_orders)
    }), 200



@delivery_men_bp.route('/delivery_capacity', methods=['GET'])
def get_delivery_capacity():
    user_id = session["user_id"]

    dcs = supabase_cli.table("delivery_capacity").select("*").eq("user_id", user_id).execute().data
    _response = {}
    for rd in dcs:
        if rd["product"] in {JACUZZI4P, JACUZZI6P}:
            _response.update({rd["product"]: rd["quantity"]})

    zones = supabase_cli.table("user_delivery_zones").select("*").eq("user_id", user_id).execute().data
    _response.update({"zones": zones})
    return jsonify(_response), 200



@delivery_men_bp.route('/delivery_capacity', methods=['PATCH'])
def patch_delivery_capacity():
    data = request.get_json()
    user_id = session["user_id"]

    j4p = {'user_id': user_id, 'product': JACUZZI4P, 'quantity': data[JACUZZI4P]}
    j6p = {'user_id': user_id, 'product': JACUZZI6P, 'quantity': data[JACUZZI6P]}

    _ = supabase_cli.table("delivery_capacity").upsert([j4p, j6p]).execute()
    return jsonify({"message": "Mise à jour réussie !"}), 200
