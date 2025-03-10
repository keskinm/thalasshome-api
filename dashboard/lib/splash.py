from flask import Blueprint, render_template, session

from dashboard.db.client import supabase_cli
from dashboard.lib.admin import get_cards

splash_bp = Blueprint("splash", __name__)


@splash_bp.route("/")
def splash():
    if not session.get("logged_in"):
        return render_template("login.html")
    else:
        context = {"is_staff": session.get("is_staff", False)}
        return render_template("delivery_men.html", **context)


@splash_bp.route("/admin.html")
def admin_index():
    if not session.get("logged_in") or not session.get("is_staff"):
        return "Accès interdit", 403

    res = get_cards()
    employee_names = supabase_cli.table("users").select("username").execute().data
    res = {
        **res,
        **{"employees": list(map(lambda x: x.get("username"), employee_names))},
    }

    return render_template("admin.html", **res)
