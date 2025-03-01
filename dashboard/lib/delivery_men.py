from flask import request, session, Blueprint, jsonify

from dashboard.constants import JACUZZI6P, JACUZZI4P
from dashboard.db.client import supabase_cli
delivery_men_bp = Blueprint('delivery_men', __name__)



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
