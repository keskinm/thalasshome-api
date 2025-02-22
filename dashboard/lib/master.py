import random
import os
from google.cloud import datastore
import json
import hmac
import hashlib
import base64
from flask import flash, render_template, request, session, flash, jsonify

from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.orm import sessionmaker

from sqlalchemy import create_engine
from dashboard.db.tabledef import User

from dashboard.lib.patch.hooks import Hooks
from dashboard.lib.handler.creation_order.creation_order import CreationOrderHandler
from dashboard.utils.maps.maps import zip_codes_to_locations
from dashboard.lib.notifier.notifier import Notifier
from dashboard.lib.utils.utils import find_zone
from dashboard.db.queries import Queries
from dashboard.lib.parser.creation_order.creation_order import CreationOrderParser

engine = create_engine('sqlite:///providers.db', echo=True)


client = datastore.Client()


class Master:
    def __init__(self):
        self.secure_hooks = Hooks()
        self.notifier = Notifier()

    @staticmethod
    def select_employee(item):
        command_country = item['shipping_address']['country']
        command_zip = item['shipping_address']['zip']
        selected = 'None'
        found_zone = find_zone(command_zip, command_country)

        employees_by_location = Queries(User).aggregate_by_column(column_name='zone', selection='username')

        if found_zone and found_zone in employees_by_location:
            possible_list = employees_by_location[found_zone]
            selected = random.choice(possible_list)

        item['employee'] = selected
        client.put(item)  # update db

        return selected

    @staticmethod
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

    def get_cards(self, query_zone=None, query_country=None):
        query = client.query(kind="orders")
        all_keys = query.fetch()
        res = {}

        for item in all_keys:
            zipcode = item['shipping_address']['zip'] if 'shipping_address' in item else None
            if self.check_zone(query_zone, query_country, zipcode):
                continue

            status = item['status'] if 'status' in item else 'ask'  # def status = ask

            if 'status' not in item:
                item['status'] = status
                client.put(item)

            if 'employee' in item:
                empl = item['employee']
            else:
                empl = self.select_employee(item)

            replace = item['replace'] if 'replace' in item else 'Aucun'

            adr = CreationOrderParser().get_address(item)
            ship, amount = CreationOrderParser().get_ship(item)

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

    def logout(self):
        session['logged_in'] = False
        return self.root()

    def root(self):
        if not session.get('logged_in'):
            print("0!")
            return render_template('login.html')
        else:
            res = self.get_cards()

            db_session = sessionmaker(bind=engine)()
            table = db_session.query(User).filter()
            employees = list(map(lambda provider: provider.username, list(table)))
            empl = {'employees': employees}

            res = {**res, **empl}

            print("1!")
            return render_template('index.html', **res)

    @staticmethod
    def render_signup():
        return render_template('signup.html')

    def signup_post(self):
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        phone_number = request.form.get('numero_de_telephone')
        country = request.form.get('country')
        zone = request.form.get('zone')

        db_session = sessionmaker(bind=engine)()

        user = db_session.query(User).filter_by(email=email).first()

        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            # return redirect(url_for('/signup_post'))
            flash('Email address already exists')
            return self.render_signup()

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, username=name, password=generate_password_hash(password, method='pbkdf2:sha256'),
                        phone_number=phone_number, country=country, zone=zone)

        # add the new user to the database
        db_session.add(new_user)
        db_session.commit()

        # return redirect(url_for('/login'))
        return self.root()

    def do_admin_login(self):
        POST_USERNAME = str(request.form['username'])
        POST_PASSWORD = str(request.form['password'])

        s = sessionmaker(bind=engine)()
        query = s.query(User).filter(User.username == POST_USERNAME).first()
        if query and check_password_hash(query.password, POST_PASSWORD):
            session['logged_in'] = True
        else:
            flash('wrong password!')
            print("wrong password")
        return self.root()
    
    def ask_zone(self):
        data = request.get_json()
        zone = data.get('zone')
        country = data.get('country')
        
        cards = self.get_cards(zone, country)
        
        return jsonify(cards)

    def patch_order_status(self):
        print("\n ----ON PATCH ORDER STATUS------ \n")
        data = request.get_json()
        print(data)
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

    def empl(self):
        return render_template('empl.html')

    @staticmethod
    def verify_webhook(data, hmac_header):
        # SECRET = 'hush'
        SECRET = 'cc226b71cdbaea95db7f42e1d05503f92282097b4fa6409ce8063b81b8727b48'
        digest = hmac.new(SECRET, data.encode('utf-8'), hashlib.sha256).digest()
        computed_hmac = base64.b64encode(digest)
        verified = hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))

        print("verified", verified)
        # if not verified:
        #     return 'fail verification of hook', 401
        #
        # return verified

    def check_availability(self):
        data = request.get_json()
        print("CHECK AVAILABILITY", data)

        # --- DO SOME STUFF TO SEE IF THE PRODUCT IS AVAILABLE ---
        return jsonify({"available": True})

    #  @todo Make gcloud compute run over https to use it through compute engine instead of gcloud app engine.
    def handle_order_creation_webhook(self):
        print("RECEIVED HOOK")
        self.secure_hooks.flush()

        data = request.get_data()
        # print("header:", request.headers)

        try:
            self.verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))
        except BaseException as e:
            print(e)

        handler = CreationOrderHandler()

        if self.secure_hooks.check_request(request):
            order = handler.parse_data(json.loads(data.decode("utf-8")))
            handler.insert_received_webhook_to_datastore(order)

            self.notifier(order)

            return 'ok', 200

        else:
            return 'you already sent me this hook!', 404
        

    def on_remove_cards(self):
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

    def on_select_repl(self):
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


    def test_notification(self):
        from dashboard.utils.samples.orders.orders import mixed_order

        datastore_client = datastore.Client()

        name = mixed_order['id']
        key = datastore_client.key("orders", name)
        c_order = datastore.Entity(key=key)
        for k, v in mixed_order.items():
            c_order[k] = v
        datastore_client.put(c_order)

        self.notifier(mixed_order)
        return self.root()


