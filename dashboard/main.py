from flask import Flask
from flask_cors import CORS

from dashboard.lib.master import Master

print("\n\n\n\n-------------------------GO !---------------------------\n\n\n\n")


app = Flask(__name__)
m = Master()

# @todo make it restrictive for obvious security reasons
CORS(app)

# @cross_origin()
# just after the @app.route or 
# cors = CORS(app, resources={r"/trying/*": {"origins": "*"}})

app.add_url_rule('/', view_func=m.root)
app.add_url_rule('/empl', view_func=m.empl)

# @todo check the "post" is correctly passed with this way
app.add_url_rule('/order_creation_webhook', view_func=m.handle_order_creation_webhook, methods=['POST'])
app.add_url_rule('/logout', view_func=m.logout, methods=['POST', 'GET'])
app.add_url_rule('/login', view_func=m.do_admin_login, methods=['POST'])
app.add_url_rule('/signup', view_func=m.render_signup, methods=['POST', 'GET'])
app.add_url_rule('/signup_post', view_func=m.signup_post, methods=['POST'])


import os

# @todo used in the login tutorial, investigate what's the utility of this?
app.secret_key = os.urandom(12)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)


entry_command = 'gunicorn -b 0.0.0.0:8000 dashboard.main:app'

