from flask import Blueprint, render_template, session

from dashboard.container import container

splash_bp = Blueprint("splash", __name__)


@splash_bp.route("/")
def splash():
    if not session.get("logged_in"):
        return render_template("login.html")
    else:
        context = {"is_staff": session.get("is_staff", False)}
        return render_template("delivery_men.html", **context)
