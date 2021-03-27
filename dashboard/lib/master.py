import random
import os
from google.cloud import datastore
import json
import hmac
import hashlib
import base64
from flask import Flask, flash, redirect, render_template, request, session, abort


from dashboard.lib.patch.hooks import Hooks
from dashboard.lib.handler.creation_order.creation_order import CreationOrderHandler
from dashboard.utils.maps.maps import zip_codes_to_locations, employees_to_location, employees


client = datastore.Client()


class Master:
    def __init__(self):
        self.secure_hooks = Hooks()

    @staticmethod
    def find_zone(zip, country):
        for zone, v in zip_codes_to_locations[country].items():
            for z_prefix in v:
                if zip.startswith(z_prefix):
                    return zone
        return None

    def select_employee(self, item):
        country = item['shipping_address']['country']
        zip = item['shipping_address']['zip']
        selected = 'None'
        found_zone = self.find_zone(zip, country)

        if found_zone and found_zone in employees_to_location:
            possible_list = employees_to_location[found_zone]
            selected = random.choice(possible_list)

        item['employee'] = selected
        client.put(item)  # update db

        return selected

    @staticmethod
    def check_zone(query_zone, query_country, zip):
        if not query_zone or not query_country:
            return False

        zips = zip_codes_to_locations[query_country][query_zone]
        for z in zips:
            if zip.startswith(z):
                return False

        return True

    def get_cards(self, query_zone=None, query_country=None):
        query = client.query(kind="orders")
        all_keys = query.fetch()
        res = {}

        for item in all_keys:
            status = item['status'] if 'status' in item else 'ask'  # def status = ask

            if 'status' not in item:
                item['status'] = status
                client.put(item)

            if 'employee' in item:
                empl = item['employee']
            else:
                empl = self.select_employee(item)

            replace = item['replace'] if 'replace' in item else 'Aucun'

            adr_item = item['shipping_address']
            adr = ' '.join([adr_item['city'], adr_item['zip'], adr_item['address1'], adr_item['address2']])

            if self.check_zone(query_zone, query_country, adr_item['zip']):
                continue

            ship = ""

            if 'line_items' in item:
                d_items = item['line_items']
                for start_separator, d_i in enumerate(d_items):
                    ship += " --+-- " if start_separator else ''
                    ship += d_i['name'] + " "
                    if d_i['properties']:
                        prop = {p['name']: p['value'] for p in d_i['properties']}
                        ship += ' '.join(
                            ['Du', prop['From'], prop['start-time'], '  Au', prop['To'], prop['finish-time']]).\
                            replace("\\", "")

            else:
                ship += "Aucun"

            res.setdefault(status, [])
            res[status].append({
                'address': adr,
                'def_empl': empl,
                'rep_empl': replace,
                'shipped': ship,
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
            env_variables = {k: os.getenv(k) for k in ['ws_address']}

            empl = {'employees': employees}

            res = {**res, **env_variables, **empl}

            print("1!")
            return render_template('index.html', **res)

    def do_admin_login(self):
        from sqlalchemy.orm import sessionmaker
        from dashboard.db.dummy import engine, User

        POST_USERNAME = str(request.form['username'])
        POST_PASSWORD = str(request.form['password'])

        Session = sessionmaker(bind=engine)
        s = Session()
        query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]))
        result = query.first()
        if result:
            session['logged_in'] = True
        else:
            flash('wrong password!')
        return self.root()

    def empl(self):
        res = self.get_cards()
        return render_template('empl.html', **res)

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

    #  @todo debug why not working on compute engine mode (works only with google app)
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

            print("ok ;)")

            #  update currently connected clients

            # sio = socketio.Client()
            # sio.connect(f'https://{os.getenv("ws_address")}/')
            # sio.emit('trigger_update', {'key': 'update'})
            return 'ok', 200

        else:
            return 'you already sent me this hook!', 404
