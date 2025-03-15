from flask import Blueprint, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from dashboard.container import container

SUPABASE_CLI = container.get("SUPABASE_CLI")
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    POST_EMAIL = str(
        request.form["username"]
    )  # form field still named "username" for compatibility
    POST_PASSWORD = str(request.form["password"])

    response = (
        SUPABASE_CLI.table("users")
        .select("*")
        .eq("email", POST_EMAIL)
        .maybe_single()
        .execute()
    )

    if response:
        data = response.data
    else:
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

    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    phone_number = request.form.get("numero_de_telephone")

    user = (
        SUPABASE_CLI.table("users")
        .select("*")
        .eq("email", email)
        .maybe_single()
        .execute()
    )

    if (
        user is not None
    ):  # if a user is found, we want to redirect back to signup page so user can try again
        flash("Email address already exists")
        return render_signup()

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = {
        "email": email,
        "username": name,
        "password": generate_password_hash(password, method="pbkdf2:sha256"),
        "phone_number": phone_number,
    }

    SUPABASE_CLI.table("users").insert(new_user).execute()

    return splash()
