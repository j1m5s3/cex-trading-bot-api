import os
from datetime import datetime
from docker import DockerClient
from flask import current_app, make_response, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from db.mongo_interface import MongoInterface

from routes.schemas.base import BaseResponseSchema
from routes.schemas.bot_schema import DeployPOSTRequestSchema
from routes.utils.auth_utils import document_login_required
from routes.utils.file_utils import replace_placeholder_env_values_with_user

bot_blueprint = Blueprint(
    'bot',
    __name__,
    url_prefix='/bot',
    description='Bot API read/writes/deploy/kill'
)


@bot_blueprint.route('/deploy')
class BotsView(MethodView):
    #@jwt_required
    #@document_login_required
    @bot_blueprint.arguments(schema=DeployPOSTRequestSchema, location='json')
    @bot_blueprint.response(status_code=200, schema=BaseResponseSchema)
    def post(self, data):
        """
        Deploy bot
        """
        user_id = "test"
        docker_client: DockerClient = current_app.extensions['docker_client']

        # Step 1: Check if user at max bots
        # Step 2: Create env file from user input
        # Step 3: Build bot image from base image
        # Step 4: Run bot container
        # Step 5: Save bot container id to user document and increment bot count

        try:
            user_docker_file = replace_placeholder_env_values_with_user(user_env=data["user_env"], user_id=user_id)
            docker_file_path_abs = os.path.abspath(user_docker_file)
            base_path = os.path.dirname(docker_file_path_abs) + "/"

            user_tag = f"{user_id}-{data['asset_id']}-{int(datetime.now().timestamp())}".lower()
            result = docker_client.images.build(path=base_path, dockerfile=docker_file_path_abs, tag=user_tag)
            current_app.logger.info(f"Built image: {result}")

            container = docker_client.containers.run(image=user_tag, detach=True, name=user_tag, network="host")
            current_app.logger.info(f"Running container: {container}")
        except Exception as e:
            current_app.logger.info(f"Error deploying bot: {e}")

        return {"data": "Bot deployed successfully"}