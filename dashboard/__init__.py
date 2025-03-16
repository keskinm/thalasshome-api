import os

import yaml
from flask import Flask
from flask_cors import CORS

from dashboard.constants import ENV_DIR, REQUIRED_VARIABLES
from dashboard.lib.logging_config import setup_logging


def load_yaml_env(path_to_yaml):
    """Load env_variables from a local YAML file and set them into os.environ."""
    try:
        with open(path_to_yaml, "r") as f:
            data = yaml.safe_load(f)
        env_vars = data.get("env_variables", {})
        for k, v in env_vars.items():
            os.environ[k] = v
    except Exception as e:
        print(f"Could not load env vars from {path_to_yaml}: {e}")


# Load from danger.yaml
load_yaml_env(ENV_DIR / "danger.yaml")


def create_app(testing=False):
    setup_logging(testing)

    from dashboard.registerer import EOF_REGISTERER

    for var in REQUIRED_VARIABLES:
        if var not in os.environ:
            raise Exception(f"Required environment variable {var} is missing")

    app = Flask(__name__)

    if testing:
        app.config["TESTING"] = True

    from dashboard.lib.admin import admin_bp
    from dashboard.lib.auth import auth_bp
    from dashboard.lib.delivery_men import delivery_men_bp
    from dashboard.lib.notifier import notifier_bp
    from dashboard.lib.services import services_bp
    from dashboard.lib.splash import splash_bp

    app.register_blueprint(splash_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(notifier_bp, url_prefix="/notifier")
    app.register_blueprint(services_bp, url_prefix="/services")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(delivery_men_bp, url_prefix="/delivery_men")

    # @todo make it restrictive
    CORS(app)

    app.secret_key = os.urandom(12)

    return app
