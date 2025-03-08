from flask import Blueprint, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from dashboard.db.client import supabase_cli
from dashboard.lib.hooks import Hooks

secure_hooks = Hooks()


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    POST_USERNAME = str(request.form["username"])
    POST_PASSWORD = str(request.form["password"])

    response = (
        supabase_cli.table("users")
        .select("*")
        .eq("username", POST_USERNAME)
        .maybe_single()
        .execute()
    )

    if response:
        data = response.data
    else:
        flash("wrong username")
        return "wrong username"

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
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    phone_number = request.form.get("numero_de_telephone")
    country = request.form.get("country")
    zone = request.form.get("zone")

    user = (
        supabase_cli.table("users")
        .select("*")
        .eq("email", email)
        .limit(1)
        .single()
        .execute()
    ).data

    if (
        user
    ):  # if a user is found, we want to redirect back to signup page so user can try again
        # return redirect(url_for('/signup_post'))
        flash("Email address already exists")
        return render_signup()

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = {
        "email": email,
        "username": name,
        "password": generate_password_hash(password, method="pbkdf2:sha256"),
        "phone_number": phone_number,
        "country": country,
        "zone": zone,
    }

    supabase_cli.table("users").insert(new_user).execute()

    return splash()
