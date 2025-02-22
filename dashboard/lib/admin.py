import random
from google.cloud import datastore
import hmac
import hashlib
import base64
from flask import render_template, request, session, flash, jsonify, Blueprint, redirect
from dashboard.db.client import supabase_cli

from werkzeug.security import generate_password_hash


from dashboard.lib.hooks import Hooks
from dashboard.utils.maps.maps import zip_codes_to_locations
from dashboard.lib.locations import find_zone
from dashboard.lib.order import OrderParser

from werkzeug.security import check_password_hash


client = datastore.Client()
secure_hooks = Hooks()


admin_bp = Blueprint('admin', __name__)


def select_employee(item):
    command_country = item['shipping_address']['country']
    command_zip = item['shipping_address']['zip']
    selected = 'None'
    found_zone = find_zone(command_zip, command_country)

    if found_zone:
        employees = supabase_cli.rpc("get_user_by_zone", {"command_zone": found_zone}).execute().data
        if employees:
            selected = random.choice(employees)["username"]

    item['employee'] = selected
    client.put(item)

    return selected


def check_zone(query_zone, query_country, zipcode):
    if zipcode is None:
        return True

    if not query_zone or not query_country:
        return False

    zips = zip_codes_to_locations[query_country][query_zone]
    for z in zips:
        if zipcode.startswith(z):
            return False

    return True


def get_cards(query_zone=None, query_country=None):
    query = client.query(kind="orders")
    all_keys = query.fetch()
    res = {}

    for item in all_keys:
        zipcode = item['shipping_address']['zip'] if 'shipping_address' in item else None
        if check_zone(query_zone, query_country, zipcode):
            continue

        status = item['status'] if 'status' in item else 'ask'  # def status = ask

        if 'status' not in item:
            item['status'] = status
            client.put(item)

        if 'employee' in item:
            empl = item['employee']
        else:
            empl = select_employee(item)

        replace = item['replace'] if 'replace' in item else 'Aucun'

        adr = OrderParser().get_address(item)
        ship, amount = OrderParser().get_ship(item)

        res.setdefault(status, [])
        res[status].append({
            'address': adr,
            'def_empl': empl,
            'rep_empl': replace,
            'shipped': ship,
            'amount': amount,
            'ent_id': item.id,
        })

    return res

@admin_bp.route('/')
def root():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        res = get_cards()
        employee_names = supabase_cli.table("users").select("username").execute().data
        res = {**res, **{'employees': list(map(lambda x: x.get('username'), employee_names))}}

        return render_template('index.html', **res)

@admin_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session['logged_in'] = False
    return root()

@admin_bp.route('/signup', methods=['POST', 'GET'])
def render_signup():
    return render_template('signup.html')

@admin_bp.route('/signup_post', methods=['POST'])
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

    return root()

@admin_bp.route('/ask_zone', methods=['POST'])
def ask_zone():
    data = request.get_json()
    zone = data.get('zone')
    country = data.get('country')

    cards = get_cards(zone, country)

    return jsonify(cards)


@admin_bp.route('/order/status', methods=['PATCH'])
def patch_order_status():
    data = request.get_json()
    item_id = int(data['item'])
    query = client.query(kind="orders")
    query.add_filter("__key__", "=", client.key('orders', item_id))
    orders = query.fetch()

    for order in orders:
        order['status'] = data['category']

        if order['status'] not in ['ask', 'delivery', 'client', 'stock', 'done', 'canceled']:
            print(f"{order['status']} not in ['ask', 'delivery', 'client', 'stock', 'done', 'canceled'], "
                  f"continuing")
            continue

        client.put(order)
    return jsonify({"message": "Order status updated"})


@admin_bp.route('/empl')
def empl():
    return render_template('empl.html')


def verify_webhook(data, hmac_header):
    # SECRET = 'hush'
    SECRET = 'cc226b71cdbaea95db7f42e1d05503f92282097b4fa6409ce8063b81b8727b48'
    digest = hmac.new(SECRET, data.encode('utf-8'), hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    verified = hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))
    return verified


@admin_bp.route('/remove_cards', methods=['POST'])
def on_remove_cards():
    data = request.get_json()
    list_id = data['list_id']
    print("\n ----ON REMOVE CARDS------ \n")

    query = client.query(kind="orders")
    query.add_filter("status", "=", list_id)
    orders = query.fetch()

    for order in orders:
        client.delete(order.key)
    return jsonify({
        "message": "Cards removed from list",
        "list_id": list_id
    })

@admin_bp.route('/select_repl', methods=['POST'])
def on_select_repl():
    data = request.get_json()
    select_label = data['select_label']
    item_id = data['item_id']

    query = client.query(kind="orders")
    query.add_filter("__key__", "=", client.key('orders', int(item_id)))
    orders = query.fetch()

    for order in orders:
        order['replace'] = select_label
        client.put(order)
    return jsonify({"message": "Replacement updated",
                    "item_id": item_id,
                    "replace": select_label})


@admin_bp.route('/login', methods=['POST'])
def do_admin_login():
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
        return redirect('/')
    else:
        flash('wrong password!')
        print("wrong password")
        return redirect('/login')
