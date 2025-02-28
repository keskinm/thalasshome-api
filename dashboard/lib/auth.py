from flask import render_template, request, session, flash, Blueprint, redirect
from dashboard.db.client import supabase_cli

from werkzeug.security import generate_password_hash

from dashboard.lib.hooks import Hooks

from werkzeug.security import check_password_hash


secure_hooks = Hooks()


auth_bp = Blueprint('auth', __name__)





@auth_bp.route('/')
def splash():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        context = {"is_staff": session.get("is_staff", False)}
        return render_template('delivery_men.html', **context)



@auth_bp.route('/login', methods=['POST'])
def login():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    response = (
        supabase_cli.table("users")
        .select("*")
        .eq("username", POST_USERNAME)
        .maybe_single()
        .execute()
    ).data

    if response and check_password_hash(response["password"], POST_PASSWORD):
        session['logged_in'] = True
        session["is_staff"] = response["is_staff"]
        return redirect('/')
    else:
        flash('wrong password!')
        print("wrong password")
        return redirect('/login')



@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session['logged_in'] = False
    return splash()


@auth_bp.route('/signup', methods=['POST', 'GET'])
def render_signup():
    return render_template('signup.html')


@auth_bp.route('/signup_post', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    phone_number = request.form.get('numero_de_telephone')
    country = request.form.get('country')
    zone = request.form.get('zone')

    user = (
        supabase_cli.table("users")
        .select("*")
        .eq("email", email)
        .limit(1)
        .single()
        .execute()
    ).data

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        # return redirect(url_for('/signup_post'))
        flash('Email address already exists')
        return render_signup()

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = {"email": email,
                "username": name,
                "password": generate_password_hash(password, method='pbkdf2:sha256'),
                "phone_number": phone_number,
                "country": country,
                "zone": zone}

    supabase_cli.table("users").insert(new_user).execute()

    return splash()

