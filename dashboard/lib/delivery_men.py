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
    return jsonify(_response), 200



@delivery_men_bp.route('/delivery_capacity', methods=['PATCH'])
def patch_delivery_capacity():
    data = request.get_json()
    user_id = session["user_id"]

    j4p = {'user_id': user_id, 'product': JACUZZI4P, 'quantity': data[JACUZZI4P]}
    j6p = {'user_id': user_id, 'product': JACUZZI6P, 'quantity': data[JACUZZI6P]}

    _ = supabase_cli.table("delivery_capacity").upsert([j4p, j6p]).execute()
    return jsonify({"message": "Mise à jour réussie !"}), 200



# ----------------------------



@delivery_men_bp.route('/delivery_zones', methods=['GET'])
def list_zones():
    user_id = session["user_id"]
    zones = supabase_cli.table("user_delivery_zones").select("*").eq("user_id", user_id).execute().data
    return jsonify(zones), 200

@delivery_men_bp.route('/delivery_zones', methods=['POST'])
def create_zone():
    """
    Expects JSON:
    {
      "zone_name": "My zone",
      "lat": 48.8566,
      "lon": 2.3522,
      "radius_km": 30
    }
    """
    user_id = session["user_id"]
    data = request.get_json()

    zone_name = data.get('zone_name')
    lat = data.get('lat')
    lon = data.get('lon')
    radius = data.get('radius_km', 30)

    # Build WKT for the geography, if lat/lon are provided
    center_geog = None
    if lat is not None and lon is not None:
        center_geog = f"SRID=4326;POINT({lon} {lat})"

    row = {
        'user_id': user_id,
        'zone_name': zone_name,
        'radius_km': radius
    }
    if center_geog:
        row['center_geog'] = center_geog

    resp = supabase_cli.table("user_delivery_zones").insert(row).execute()

    if not resp.data:
        return jsonify({"error": "Insert failed or returned no data"}), 400

    return jsonify({"message": "Zone created"}), 201


@delivery_men_bp.route('/delivery_zones/<int:zone_id>', methods=['PATCH'])
def update_zone(zone_id):
    """
    Expects JSON, e.g.:
    {
      "zone_name": "New name",
      "lat": 46.0,
      "lon": 3.1,
      "radius_km": 50
    }
    """
    user_id = session["user_id"]
    data = request.get_json()

    update_data = {}
    if 'zone_name' in data:
        update_data['zone_name'] = data['zone_name']
    if 'radius_km' in data:
        update_data['radius_km'] = data['radius_km']

    lat = data.get('lat')
    lon = data.get('lon')
    if lat is not None and lon is not None:
        update_data['center_geog'] = f"SRID=4326;POINT({lon} {lat})"

    resp = supabase_cli.table("user_delivery_zones").update(update_data).match({
        "id": zone_id,
        "user_id": user_id
    }).execute()

    if resp.error:
        return jsonify({"error": resp.error.message}), 400
    return jsonify({"message": "Zone updated"}), 200

@delivery_men_bp.route('/delivery_zones/<int:zone_id>', methods=['DELETE'])
def delete_zone(zone_id):
    user_id = session["user_id"]
    resp = supabase_cli.table("user_delivery_zones") \
                       .delete() \
                       .match({"id": zone_id, "user_id": user_id}) \
                       .execute()
    if resp.error:
        return jsonify({"error": resp.error.message}), 400
    return jsonify({"message": "Zone deleted"}), 200