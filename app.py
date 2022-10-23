import os
from typing import Optional

from flask import Flask
from flask_smorest import Api

from db import db
import models

from controllers.item import blp as item_blueprint
from controllers.store import blp as store_blueprint


def create_app(db_url: Optional[str] = None):
    app = Flask(__name__)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_NOTIFICATIONS"] = False

    db.init_app(app)  # connect Flask app with SQLAlchemy

    api = Api(app)

    with app.app_context():
        db.create_all()

    api.register_blueprint(item_blueprint)
    api.register_blueprint(store_blueprint)
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
