import os

from flask import Flask, jsonify

from .models import db
from .routes import api


def create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///library.db")
    app.config["JSON_AS_ASCII"] = False
    if config:
        app.config.update(config)

    db.init_app(app)
    app.register_blueprint(api)

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "not found"}), 404

    with app.app_context():
        db.create_all()
    return app
