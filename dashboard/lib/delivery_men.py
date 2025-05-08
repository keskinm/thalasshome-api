from flask import Blueprint, jsonify, request, session

from dashboard.constants import JACUZZI4P, JACUZZI6P
from dashboard.container import container
from dashboard.lib.order.order import get_address, get_ship

delivery_men_bp = Blueprint("delivery_men", __name__)


@delivery_men_bp.route("/orders", methods=["GET"])
def get_orders():
    user_id = session["user_id"]

    available_orders = container.get("DB_CLIENT").select_from_table(
        "orders",
        select_columns="*",
        conditions={"delivery_men_id": None, "status": "ask"},
    )

    ongoing_orders = container.get("DB_CLIENT").select_from_table(
        "orders",
        select_columns="*",
        conditions={"delivery_men_id": user_id, "status": ["assigned", "in_delivery"]},
    )

    completed_orders = container.get("DB_CLIENT").select_from_table(
        "orders",
        select_columns="*",
        conditions={"delivery_men_id": user_id, "status": "delivered"},
        limit=10,
        order_by="updated_at",
        desc=True,
    )

    def process_orders(orders):
        results = []
        for order in orders:
            line_items = container.get("DB_CLIENT").select_from_table(
                "line_items", select_columns="*", conditions={"order_id": order["id"]}
            )
            ship, amount = get_ship(line_items)
            results.append(
                {
                    "id": order["id"],
                    "address": get_address(order),
                    "phone": order["shipping_phone"],
                    "ship": ship,
                    "amount": amount,
                }
            )
        return results

    return (
        jsonify(
            {
                "available": process_orders(available_orders),
                "ongoing": process_orders(ongoing_orders),
                "completed": process_orders(completed_orders),
            }
        ),
        200,
    )


@delivery_men_bp.route("/orders/<int:order_id>/complete", methods=["POST"])
def complete_order(order_id):
    """Mark an order as delivered"""
    user_id = session["user_id"]

    try:
        resp = container.get("DB_CLIENT").update_table(
            "orders",
            {"status": "delivered", "updated_at": "now()"},
            conditions={"id": order_id, "delivery_men_id": user_id},
        )

        if not resp:
            return jsonify({"error": "Update failed or no matching order"}), 400

        return jsonify({"message": "Order marked as delivered"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@delivery_men_bp.route("/delivery_capacity", methods=["GET"])
def get_delivery_capacity():
    user_id = session["user_id"]

    dcs = container.get("DB_CLIENT").select_from_table(
        "delivery_capacity", select_columns="*", conditions={"user_id": user_id}
    )
    _response = {}
    for rd in dcs:
        if rd["product"] in {JACUZZI4P, JACUZZI6P}:
            _response.update({rd["product"]: rd["quantity"]})
    return jsonify(_response), 200


@delivery_men_bp.route("/delivery_capacity", methods=["PATCH"])
def patch_delivery_capacity():
    data = request.get_json()
    user_id = session["user_id"]

    j4p = {"user_id": user_id, "product": JACUZZI4P, "quantity": data[JACUZZI4P]}
    j6p = {"user_id": user_id, "product": JACUZZI6P, "quantity": data[JACUZZI6P]}

    _ = container.get("DB_CLIENT").insert_into_table("delivery_capacity", [j4p, j6p])
    return jsonify({"message": "Mise à jour réussie !"}), 200


# ----------------------------


@delivery_men_bp.route("/delivery_zones", methods=["GET"])
def list_zones():
    user_id = session["user_id"]
    zones = container.get("DB_CLIENT").select_from_table(
        "user_delivery_zones", select_columns="*", conditions={"user_id": user_id}
    )
    return jsonify(zones), 200


@delivery_men_bp.route("/delivery_zones", methods=["POST"])
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

    zone_name = data.get("zone_name")
    lat = data.get("lat")
    lon = data.get("lon")
    radius = data.get("radius_km", 30)

    # Build WKT for the geography, if lat/lon are provided
    center_geog = None
    if lat is not None and lon is not None:
        center_geog = f"SRID=4326;POINT({lon} {lat})"

    row = {"user_id": user_id, "zone_name": zone_name, "radius_km": radius}
    if center_geog:
        row["center_geog"] = center_geog

    resp = container.get("DB_CLIENT").insert_into_table("user_delivery_zones", row)

    if not resp:
        return jsonify({"error": "Insert failed or returned no data"}), 400

    return jsonify({"message": "Zone created"}), 201


@delivery_men_bp.route("/delivery_zones/<int:zone_id>", methods=["PATCH"])
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
    if "zone_name" in data:
        update_data["zone_name"] = data["zone_name"]
    if "radius_km" in data:
        update_data["radius_km"] = data["radius_km"]

    lat = data.get("lat")
    lon = data.get("lon")
    if lat is not None and lon is not None:
        update_data["center_geog"] = f"SRID=4326;POINT({lon} {lat})"

    try:
        resp = container.get("DB_CLIENT").update_table(
            "user_delivery_zones",
            update_data,
            conditions={"id": zone_id, "user_id": user_id},
        )

        if not resp:
            return jsonify({"error": "Update failed or no matching zone"}), 400

        return jsonify({"message": "Zone updated"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@delivery_men_bp.route("/delivery_zones/<int:zone_id>", methods=["DELETE"])
def delete_zone(zone_id):
    user_id = session["user_id"]

    try:
        success = container.get("DB_CLIENT").delete_from_table(
            "user_delivery_zones", conditions={"id": zone_id, "user_id": user_id}
        )

        if not success:
            return jsonify({"error": "Zone not found"}), 404

        return jsonify({"message": "Zone deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
