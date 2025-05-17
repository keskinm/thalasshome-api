from flask import Blueprint, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from dashboard.container import container

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    POST_EMAIL = str(
        request.form["username"]
    ).lower()  # form field still named "username" for compatibility
    POST_PASSWORD = str(request.form["password"])

    data = container.get("DB_CLIENT").select_from_table(
        "users", conditions={"email": POST_EMAIL}, maybe_single=True
    )

    if not data:
        flash("Email not found")
        return "Email not found"

    if check_password_hash(data["password"], POST_PASSWORD):
        session["logged_in"] = True
        session["is_staff"] = data["is_staff"]
        session["user_id"] = data["id"]
        return redirect("/")
    else:
        return "wrong password"


@auth_bp.route("/logout", methods=["POST", "GET"])
def logout():
    session["logged_in"] = False
    from dashboard.lib.splash import splash

    return splash()


@auth_bp.route("/signup", methods=["POST", "GET"])
def render_signup():
    return render_template("signup.html")


@auth_bp.route("/signup_post", methods=["POST"])
def signup_post():
    from dashboard.lib.splash import splash

    email = request.form.get("email").lower()
    name = request.form.get("name")
    password = request.form.get("password")
    phone_number = request.form.get("numero_de_telephone")

    user = container.get("DB_CLIENT").select_from_table(
        "users", conditions={"email": email}, maybe_single=True
    )

    if user is not None:
        flash("Email address already exists")
        return render_signup()

    new_user = {
        "email": email,
        "username": name,
        "password": generate_password_hash(password, method="pbkdf2:sha256"),
        "phone_number": phone_number,
    }

    container.get("DB_CLIENT").insert_into_table("users", new_user)

    return splash()
