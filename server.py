from flask import Flask, render_template, request
import pymongo
import os 
import json

print(os.getcwd())


MONGODB_URL = os.environ['MONGODB_URL']
MONGODB_NAME = os.environ['MONGODB_NAME']
MONGO_JS_PROJECT_IM_PATHS = os.environ['MONGO_JS_PROJECT_IM_PATHS']
MONGO_JS_PROJECT_L_PATHS = os.environ['MONGO_JS_PROJECT_L_PATHS']

client = pymongo.MongoClient(MONGODB_URL)
collections = client[MONGODB_NAME]
js_project_im_paths = collections[MONGO_JS_PROJECT_IM_PATHS]
js_project_l_paths = collections[MONGO_JS_PROJECT_L_PATHS]


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def homepage():
        return render_template('index.html')

    @app.route('/scripts.js')
    def script():
        return render_template('scripts.js', color='pink')


    @app.route('/trying/', methods=['GET','POST'])
    def trying():
        if request.method == "POST":
            kwargs = json.loads(request.form.get('data'))
            print(kwargs)
            return {"success": True}


    return app


create_app().run(host='192.168.1.29', port=5000)


