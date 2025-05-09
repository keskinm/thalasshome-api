import logging
import urllib.parse

from flask import Blueprint, jsonify, render_template, request, session

from dashboard.constants import JACUZZI4P, JACUZZI6P
from dashboard.container import container
from dashboard.lib.notifier import Notifier
from dashboard.lib.order.order import get_address, get_name, get_ship

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


@delivery_men_bp.route("/orders/<token_id>/accept", methods=["GET"])
def accept_order_route(token_id):
    """Show confirmation page for accepting an order"""
    decoded_token = urllib.parse.unquote(token_id)
    order_id, provider_username = decoded_token.split("|")

    order = container.get("DB_CLIENT").select_from_table(
        "orders", select_columns="*", conditions={"id": order_id}, maybe_single=True
    )

    error = None
    if order is None:
        error = "La commande n'existe plus."
    elif order["delivery_men_id"]:
        error = "La commande a déjà été acceptée par un autre livreur."
        provider = container.get("DB_CLIENT").select_from_table(
            "users",
            select_columns="*",
            conditions={"username": provider_username},
            limit=1,
            single=True,
        )
        if provider and order["delivery_men_id"] == provider["id"]:
            error = "Vous avez déjà accepté cette commande."

    return render_template(
        "notification/confirm_accept.html", error=error, token_id=token_id
    )


@delivery_men_bp.route("/orders/<token_id>/accept", methods=["POST"])
def accept_order_post(token_id):
    """Actually accept the order after confirmation"""
    return accept_order(token_id)


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
    try:
        data = request.get_json()
        user_id = session["user_id"]

        j4p = {"user_id": user_id, "product": JACUZZI4P, "quantity": data[JACUZZI4P]}
        j6p = {"user_id": user_id, "product": JACUZZI6P, "quantity": data[JACUZZI6P]}

        # Use upsert with user_id and product as unique columns
        _ = container.get("DB_CLIENT").upsert_into_table(
            "delivery_capacity", [j4p, j6p], unique_columns=["user_id", "product"]
        )
        return jsonify({"message": "Mise à jour réussie !"}), 200
    except Exception as e:
        logging.error("Error updating delivery capacity: %s", str(e))
        return (
            jsonify(
                {"error": "Erreur lors de la mise à jour de la capacité de livraison"}
            ),
            500,
        )


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


#  ----------------------------


def accept_order(token_id, flask_address=""):
    """Accept a command from a delivery person"""
    logging.info("Accepting order with token: %s", token_id)

    notifier = Notifier(flask_address=flask_address)
    decoded_token = urllib.parse.unquote(token_id)
    order_id, provider_username = decoded_token.split("|")

    order = container.get("DB_CLIENT").select_from_table(
        "orders",
        select_columns="*",
        conditions={"id": order_id},
        single=True,
        maybe_single=True,
    )

    if order is None:
        return "La commande n'existe plus."
    elif order["delivery_men_id"]:
        return "La commande a déjà été accepté par un autre livreur."

    delivery_men = container.get("DB_CLIENT").select_from_table(
        "users",
        select_columns="*",
        conditions={"username": provider_username},
        limit=1,
        single=True,
    )
    line_items = container.get("DB_CLIENT").select_from_table(
        "line_items",
        select_columns="*",
        conditions={"order_id": order_id},
    )

    delivery_men_email = delivery_men["email"]

    container.get("DB_CLIENT").update_table(
        "orders",
        {"delivery_men_id": delivery_men["id"], "status": "assigned"},
        conditions={"id": order_id},
    )

    plain_customer_name = get_name(order)

    order_email = order.get("email", "")
    template_vars = {
        "phone": order.get("phone", ""),
        "email": order_email,
        "customer_name": plain_customer_name,
    }

    text_template = notifier.jinja_env.get_template("command_accepted.txt")
    html_template = notifier.jinja_env.get_template("command_accepted.html")

    text = text_template.render(**template_vars)
    html = html_template.render(**template_vars)

    subject = "Détails sur votre commande ThalassHome"
    notifier.send_mail(delivery_men_email, subject, html, text)

    notifier.notify_customer(delivery_men, order_email)
    notifier.notify_admins(order, delivery_men, line_items)

    return """La prise en charge de la commande a bien été accepté. Vous recevrez très prochainement un mail
    contenant des informations supplémentaires pour votre commande. A bientôt ! """


def get_delivery_mens(order, test=False) -> list[dict]:
    lat, lon = order["shipping_lat"], order["shipping_lon"]

    delivery_mens = container.get("DB_CLIENT").call_rpc(
        "check_delivery_men_around_point",
        {
            "in_shipping_lon": lon,
            "in_shipping_lat": lat,
        },
    )
    if test:
        delivery_mens = list(filter(lambda x: "neuneu" in x["email"], delivery_mens))
    return delivery_mens
