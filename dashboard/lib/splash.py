from flask import Blueprint, render_template, session

from dashboard.container import container
from dashboard.lib.admin import get_cards

SUPABASE_CLI = container.get("SUPABASE_CLI")


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

    cards = get_cards()
    employee_names = SUPABASE_CLI.table("users").select("username").execute().data
    res = {
        **cards,
        **{"employees": list(map(lambda x: x.get("username"), employee_names))},
    }

    return render_template("admin.html", **res)
