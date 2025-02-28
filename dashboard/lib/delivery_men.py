from flask import request, session, Blueprint

from dashboard.constants import JACUZZI6P, JACUZZI4P
from dashboard.db.client import supabase_cli
delivery_men_bp = Blueprint('delivery_men', __name__)



@delivery_men_bp.route('/delivery_capacity', methods=['PATCH'])
def update_settings():
    breakpoint()
    data = request.get_json()
    user_id = session["id"]

    j4p = {JACUZZI4P: data[JACUZZI4P]}
    j2p = {JACUZZI6P: data[JACUZZI6P]}

    response = supabase_cli.table("users").update(j4p).eq("user_id", user_id).execute()
    response = supabase_cli.table("users").update(j2p).eq("user_id", user_id).execute()

    return
