import os

from flask import Flask
from flask_cors import CORS

from dashboard.lib.master import Master
from dashboard.lib.notifier import Notifier


def init_app():
    app = Flask(__name__)
    m = Master()
    notifier = Notifier()

    from dashboard.lib.admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    # @todo make it restrictive
    CORS(app)

    app.add_url_rule('/', view_func=m.root)

    app.add_url_rule('/empl', view_func=m.empl)

    # ------------------------ DASHBOARD ------------------------
    app.add_url_rule('/logout', view_func=m.logout, methods=['POST', 'GET'])
    app.add_url_rule('/signup', view_func=m.render_signup, methods=['POST', 'GET'])
    app.add_url_rule('/signup_post', view_func=m.signup_post, methods=['POST'])

    app.add_url_rule('/ask_zone', view_func=m.ask_zone, methods=['POST'])

    app.add_url_rule('/order/status', view_func=m.patch_order_status, methods=['PATCH'])

    app.add_url_rule('/remove_cards', view_func=m.on_remove_cards, methods=['POST'])
    app.add_url_rule('/select_repl', view_func=m.on_select_repl, methods=['POST'])

    app.add_url_rule('/test_notification', view_func=m.test_notification, methods=['GET'])


    # ------------------------ NOTIFIER ------------------------
    app.add_url_rule('/commands/accept/<token_id>', view_func=notifier.accept_command, methods=['GET'])


    # ------------------------ SERVICE TO SERVICE ------------------------
    app.add_url_rule('/order_creation_webhook', view_func=m.handle_order_creation_webhook, methods=['POST'])
    app.add_url_rule('/check_availability', view_func=m.check_availability, methods=['POST'])


    app.secret_key = os.urandom(12)

    return app
