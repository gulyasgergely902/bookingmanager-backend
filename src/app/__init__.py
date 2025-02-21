"""__init__"""

from flask import Flask
from .routes import bp


def create_app():
    """Create the Flask app"""
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
