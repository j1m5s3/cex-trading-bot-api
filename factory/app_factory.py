import docker
from datetime import timedelta
from flask import Flask, request
from flask_smorest import Api
from flask_cors import CORS

from utils import config, logger
from db.mongo_interface import MongoInterface


def create_flask_app() -> Flask:
    """
    Create Flask application

    :return:
    """

    app = Flask('CEX TRADING BOT API')

    # TODO: Move to separate config obj
    app.config["API_TITLE"] = "CEX TRADING BOT API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    expire_minutes = int(config['JWT_EXPIRE_MINUTES'])
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=expire_minutes)
    app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies", "json", "query_string"]
    app.config["JWT_SECRET_KEY"] = config['JWT_SECRET_KEY']
    app.config['API_SPEC_OPTIONS'] = {
        "components": {
            "securitySchemes": {
                "Bearer Auth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "Authorization",
                    "bearerFormat": "JWT",
                    "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token",
                }
            }
        },
    }

    app.logger = logger
    add_extensions(app)

    return app


def add_extensions(app: Flask) -> None:
    """

    :param app:
    :return:
    """
    app.extensions['mongo_interface'] = MongoInterface(
        db_name=config['DB_NAME'],
        connection_url=config['MONGO_CONNECTION_STRING']
    )

    app.extensions['docker_client'] = docker.from_env()
