# [START gae_python38_render_template]
# [START gae_python3_render_template]
import datetime

from flask import Flask, render_template, request
from flask_cors import CORS

import os
import json
from google.cloud import datastore
import hmac
import hashlib
import base64

from lib.handler.creation_order.creation_order import CreationOrderHandler

datastore_client = datastore.Client()


print(os.getcwd())
print("\n\n\n\n---------------------------------------------------------------\n\n\n\n")
print("GOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")

app = Flask(__name__)

# @todo make it restrictive for obvious security reasons
CORS(app)

# @cross_origin()
# just after the @app.route or 
# cors = CORS(app, resources={r"/trying/*": {"origins": "*"}})


@app.route('/')
def root():
    dummy_times = [datetime.datetime(2018, 1, 1, 10, 0, 0),
                   datetime.datetime(2018, 1, 2, 10, 30, 0),
                   datetime.datetime(2018, 1, 3, 11, 0, 0),
                   ]

    return render_template('index.html', times=dummy_times)


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
    order = handler.parse_data(data.decode("utf-8"))
    handler.insert_received_webhook_to_datastore(order)


@app.route('/posting_scripts')
def script():
    return render_template("js/myscripts.js", color='pink')


@app.route('/trying/', methods=['GET','POST'])
def trying():
    if request.method == "POST":
        try:
            kwargs = json.loads(request.form.get('data'))
            print(kwargs)

        except:
            return {'fail': True}

        return {"success": True}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
# [END gae_python3_render_template]
# [END gae_python38_render_template]
