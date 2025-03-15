import os

import yaml
from flask import Flask
from flask_cors import CORS

from dashboard.constants import REQUIRED_VARIABLES
from env import ENV_DIR


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


from dashboard import create_app


def init_app():
    return create_app()
