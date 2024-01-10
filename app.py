import argparse
from flask import request
from flask_smorest import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from utils import config
from factory.app_factory import create_flask_app

from routes.auth import auth_blueprint
from routes.bot import bot_blueprint


app = create_flask_app()
flask_api = Api(app)
jwt_manager = JWTManager(app)

CORS(app, origins=config["CORS_ORIGINS"])

flask_api.register_blueprint(auth_blueprint)
flask_api.register_blueprint(bot_blueprint)


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
    app.logger.info(f"json: {response.json}")
    app.logger.info(end_bound)

    return response


if __name__ == "__main__":
    # TODO: Add command line arguments

    app.run(
        debug=False,
        host="localhost",
        port=6900
    )