import argparse, os, platform

from flask import request
from flask_smorest import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from utils import config
from factory.app_factory import create_flask_app

from routes.auth import auth_blueprint
from routes.bot import bot_blueprint
from routes.data import data_blueprint

OS_ENV: str = os.environ.get("OS_ENV", "dev")
RUNTIME_ENV: str = os.environ.get("RUNTIME_ENV", "local")

app = create_flask_app()
flask_api = Api(app)
jwt_manager = JWTManager(app)

if OS_ENV in ["LINUX", "WINDOWS"]:
    CORS(app, origins=config["CORS_ORIGINS"])
else:
    CORS(app, origins="*")

flask_api.register_blueprint(auth_blueprint)
flask_api.register_blueprint(bot_blueprint)
flask_api.register_blueprint(data_blueprint)


@app.route("/")
def health_check():
    return {"status": "OK"}


@app.after_request
def log_request_and_response(response):
    request_bound = f"##########################-REQUEST-###########################"
    response_bound = f"##########################-RESPONSE-##########################"
    end_bound = f"##########################-END-###############################"
    # log request
    if request.method == "GET":
        app.logger.info(request_bound)
        app.logger.info(f"method: {request.method}")
        app.logger.info(f"url: {request.url}")
        app.logger.info(f"args: {request.args.__dict__}")
    if request.method == "POST":
        app.logger.info(request_bound)
        app.logger.info(f"method: {request.method}")
        app.logger.info(f"url: {request.url}")
        app.logger.info(f"json: {request.json}")

    # log response
    app.logger.info(response_bound)
    app.logger.info(f"status: {response.status}")
    try:
        app.logger.info(f"json: {response.json}")
    except Exception as e:
        app.logger.error(f"Error: {e}")
        app.logger.info(f"response: {response.text}")
    app.logger.info(end_bound)

    return response


if __name__ == "__main__":
    # TODO: Add command line arguments

    if RUNTIME_ENV == "DOCKER":
        app.run(
            debug=False,
            host="0.0.0.0",
            port=5000
        )
    else:
        if platform.system() == "Windows":
            app.run(
                debug=False,
                host="localhost",
                port=6900
            )
        else:
            app.run(
                debug=True,
                host="localhost",
                port=6900
            )