import os

from flask import Flask
from flask_cors import CORS

from dashboard.lib.master import Master
from dashboard.lib.notifier.notifier import Notifier

print("\n\n\n\n-------------------------GO !---------------------------\n\n\n\n")


app = Flask(__name__)
m = Master()
notifier = Notifier()

CORS(app)
# @todo make it restrictive
# @cross_origin()
# just after the @app.route or 
# cors = CORS(app, resources={r"/trying/*": {"origins": "*"}})

app.add_url_rule('/', view_func=m.root)
app.add_url_rule('/empl', view_func=m.empl)

app.add_url_rule('/order_creation_webhook', view_func=m.handle_order_creation_webhook, methods=['POST'])
app.add_url_rule('/logout', view_func=m.logout, methods=['POST', 'GET'])
app.add_url_rule('/login', view_func=m.do_admin_login, methods=['POST'])
app.add_url_rule('/signup', view_func=m.render_signup, methods=['POST', 'GET'])
app.add_url_rule('/signup_post', view_func=m.signup_post, methods=['POST'])

app.add_url_rule('/commands/accept/<token_id>', view_func=notifier.accept_command, methods=['GET'])
app.add_url_rule('/test_notification', view_func=notifier.test_notification, methods=['GET'])


app.secret_key = os.urandom(12)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)


entry_command = 'gunicorn -b 0.0.0.0:8000 dashboard.main:app'

