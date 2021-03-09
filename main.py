# [START gae_python38_render_template]
# [START gae_python3_render_template]
import datetime

from flask import Flask, render_template, request
from flask_cors import CORS

import pymongo
import os 
import json
from google.cloud import datastore

datastore_client = datastore.Client()


def create_and_save_order_test():
    kind = "Orders"
    name = "harcoded_id_01"
    task_key = datastore_client.key(kind, name)
    task = datastore.Entity(key=task_key)
    task["employee"] = 'mario'
    datastore_client.put(task)
create_and_save_order_test()


print(os.getcwd())

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

@app.route('/order_creation_webhook', methods=['POST'])
def handle_order_creation_webhook():
    print("IN ORDER CREATION WEBHOOK")
    data = request.get_data()
    verified = verify_webhook(data, request.headers.get('X-Shopify-Hmac-SHA256'))

    
@app.route('/posting_scripts')
def script():
    return render_template("js/myscripts.js", color='pink')

@app.route('/trying/', methods=['GET','POST'])
def trying():
    if request.method == "POST":
        try:
            kwargs = json.loads(request.form.get('data'))
            print(kwargs)

            update_quantity()
            print_quantity()
            
        except:
            return {'fail': True}

        return {"success": True}


# return app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
# [END gae_python3_render_template]
# [END gae_python38_render_template]
