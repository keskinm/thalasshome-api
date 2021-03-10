from flask import Flask, render_template, request
from flask_cors import CORS
import os
import json
import hmac
import hashlib
import base64

from lib.handler.creation_order.creation_order import CreationOrderHandler


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
    return render_template('index.html')


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
