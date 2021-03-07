# [START gae_python38_render_template]
# [START gae_python3_render_template]
import datetime

from flask import Flask, render_template, request
import pymongo
import os 
import json


"""
def create_and_save_entity():
    from google.cloud import datastore
    datastore_client = datastore.Client()
    kind = "Task"
    name = "sampletask1"
    task_key = datastore_client.key(kind, name)
    task = datastore.Entity(key=task_key)
    task["description"] = "Buy milk"
    datastore_client.put(task)
    key = datastore_client.key("Task", "sampletask1")
    task = datastore_client.get(key)
    print("done", task)
create_and_save_entity()
"""




print(os.getcwd())
# MONGODB_URL = os.environ['MONGODB_URL']
# MONGODB_NAME = os.environ['MONGODB_NAME']

# MONGODB_URL='127.0.0.1:27019'
# MONGODB_NAME='mydb'

# client = pymongo.MongoClient(MONGODB_URL)
# collections = client[MONGODB_NAME]

app = Flask(__name__)


@app.route('/')
def root():
    dummy_times = [datetime.datetime(2018, 1, 1, 10, 0, 0),
                   datetime.datetime(2018, 1, 2, 10, 30, 0),
                   datetime.datetime(2018, 1, 3, 11, 0, 0),
                   ]

    return render_template('index.html', times=dummy_times)
    
@app.route('/posting_scripts')
def script():
    return render_template("js/myscripts.js", color='pink')

@app.route('/trying/', methods=['GET','POST'])
def trying():
    if request.method == "POST":
        kwargs = json.loads(request.form.get('data'))
        print(kwargs)
        return {"success": True}


# return app

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_render_template]
# [END gae_python38_render_template]
