#  @todo replace this Flask by uwsgi

from flask import Flask, render_template, request
from flask_cors import CORS
from google.cloud import datastore

from ws import my_web_app

print("\n\n\n\n-------------------------GO !---------------------------\n\n\n\n")

app = Flask(__name__)

CORS(app)
client = datastore.Client()


# @cross_origin()
# just after the @app.route or
# cors = CORS(app, resources={r"/trying/*": {"origins": "*"}})


@app.route('/')
def root():
    my_web_app()

    print("running ws!")

    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005, debug=True)
