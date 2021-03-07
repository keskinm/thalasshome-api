from flask import Flask, render_template, request
import pymongo
import os 
import json

print(os.getcwd())


# MONGODB_URL = os.environ['MONGODB_URL']
# MONGODB_NAME = os.environ['MONGODB_NAME']

MONGODB_URL='127.0.0.1:27019'
MONGODB_NAME='mydb'

client = pymongo.MongoClient(MONGODB_URL)
collections = client[MONGODB_NAME]


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def homepage():
        return render_template('index.html')

    @app.route('/scripts_in_templates.js')
    def script():
        return render_template('scripts_in_templates.js', color='pink')

    @app.route('/trying/', methods=['GET','POST'])
    def trying():
        if request.method == "POST":
            kwargs = json.loads(request.form.get('data'))
            print(kwargs)
            return {"success": True}


    return app


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    create_app().run(host='127.0.0.1', port=8080, debug=True)


