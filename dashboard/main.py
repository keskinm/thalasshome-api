import os

from flask import Flask
from flask_cors import CORS
from dashboard.constants import REQUIRED_VARIABLES

def init_app():
    for var in REQUIRED_VARIABLES:
        if var not in os.environ:
            raise Exception(f"Required environment variable {var} is missing")

    app = Flask(__name__)

    from dashboard.lib.auth import auth_bp
    from dashboard.lib.admin import admin_bp
    from dashboard.lib.services import services_bp
    from dashboard.lib.notifier import notifier_bp
    from dashboard.lib.delivery_men import delivery_men_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(notifier_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(delivery_men_bp)


    # @todo make it restrictive
    CORS(app)

    app.secret_key = os.urandom(12)

    return app
