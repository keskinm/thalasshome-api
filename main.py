import random

from flask import Flask, render_template, request
from flask_cors import CORS
import os
import json
import hmac
import hashlib
import base64

from google.cloud import datastore

from lib.handler.creation_order.creation_order import CreationOrderHandler
from utils.maps.maps import zip_codes_to_locations, employees_to_location

print(os.getcwd())
print("\n\n\n\n---------------------------------------------------------------\n\n\n\n")
print("GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")

app = Flask(__name__)

# @todo make it restrictive for obvious security reasons
CORS(app)
client = datastore.Client()

# @cross_origin()
# just after the @app.route or 
# cors = CORS(app, resources={r"/trying/*": {"origins": "*"}})


def find_zone(zip):
    for zone, v in zip_codes_to_locations.items():
        for z_prefix in v:
            if zip.startswith(z_prefix):
                return zone
    return None


def select_employee(item):
    zip = item['shipping_address']['zip']
    selected = 'None'
    found_zone = find_zone(zip)

    if found_zone and found_zone in employees_to_location:
        possible_list = employees_to_location[found_zone]
        selected = random.choice(possible_list)

    item['employee'] = selected
    client.put(item)  # update db

    return selected

@app.route('/')
def root():
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
            empl = select_employee(item)

        replace = item['replace'] if 'replace' in item else 'Aucun'

        adr_item = item['shipping_address']
        adr = ' '.join([adr_item['city'], adr_item['zip'], adr_item['address1'], adr_item['address2']])

        ship = ""
        if 'line_items' in item:
            d_items = item['line_items']
            for d_i in d_items:
                ship += d_i['name'] + " "
                prop = {p['name']: p['value'] for p in d_i['properties']}
                ship += ' '.join([prop['From'], prop['start-time'], prop['To'], prop['finish-time']])
                ship += " "
        else:
            ship += "Aucun"

        res.setdefault(status, [])
        res[status].append({
            'address': adr,
            'def_empl': empl,
            'rep_empl': replace,
            'shipped': ship
        })
    return render_template('index.html', **res)


def verify_webhook(data, hmac_header):
    SECRET = 'hush'
    # SECRET = 'cc226b71cdbaea95db7f42e1d05503f92282097b4fa6409ce8063b81b8727b48'
    digest = hmac.new(SECRET, data.encode('utf-8'), hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    verified = hmac.compare_digest(computed_hmac, hmac_header.encode('utf-8'))
    
    print("verified", verified)
    if not verified:
        abort(401)

    return verified


@app.route('/order_creation_webhook', methods=['POST'])
def handle_order_creation_webhook():
    data = request.get_data()

    # verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))

    handler = CreationOrderHandler()

    order = None

    try:
        order = handler.parse_data(json.loads(data.decode("utf-8")))
        print("succeed in 1")
    except:
        print("fail in 1")

    try:
        order = handler.parse_data(data)
        print("succeed in 2")
    except:
        print("fail in 2")

    handler.insert_received_webhook_to_datastore(order)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
