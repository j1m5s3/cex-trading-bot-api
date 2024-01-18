import os
from datetime import datetime

import flask
from docker import DockerClient
from flask import current_app, make_response, jsonify, abort
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from db.mongo_interface import MongoInterface
from db.redis_interface import RedisInterface

from routes.schemas.base import BaseResponseSchema
from routes.schemas.bot_schema import DeployPOSTRequestSchema
from routes.utils.auth_utils import document_login_required, token_required
from routes.utils.file_utils import replace_placeholder_env_values_with_user

from utils.enums import RedisValueTypes

bot_blueprint = Blueprint(
    'bot',
    __name__,
    url_prefix='/bot',
    description='Bot API read/writes/deploy/kill'
)


@bot_blueprint.route('/deploy')
class BotsView(MethodView):
    @token_required
    @document_login_required
    @bot_blueprint.arguments(schema=DeployPOSTRequestSchema, location='json')
    @bot_blueprint.response(status_code=200, schema=BaseResponseSchema)
    def post(self, data, current_user):
        """
        Deploy bot
        """
        exclude_user_fields = ['<USER-API-KEY>', '<USER-API-SECRET>', '<USER-DISCORD-WEBHOOK-URL>']

        user_id = current_user  # TODO: Get user id from jwt token
        docker_client: DockerClient = current_app.extensions['docker_client']
        redis_interface: RedisInterface = current_app.extensions['redis_interface']

        try:
            user_docker_file, env_file = replace_placeholder_env_values_with_user(user_env=data["user_env"], user_id=user_id)
            docker_file_path_abs = os.path.abspath(user_docker_file)
            base_path = os.path.dirname(docker_file_path_abs) + "/"

            user_tag = f"{user_id}-{data['asset_id']}-{int(datetime.now().timestamp())}".lower()
            result = docker_client.images.build(path=base_path, dockerfile=docker_file_path_abs, tag=user_tag)
            current_app.logger.info(f"Built image: {result}")
            
            if os.path.exists(user_docker_file):
                os.remove(user_docker_file)
            else:
                current_app.logger.info(f"The file {user_docker_file} does not exist")
                abort(500, "Failed to remove docker file")
            if os.path.exists(env_file):
                os.remove(env_file)
            else:
                current_app.logger.info(f"The file {env_file} does not exist")
                abort(500, "Failed to remove env file")

            container = docker_client.containers.run(image=user_tag, detach=True, name=user_tag, network="host")

            id = container.id

            running_container = docker_client.containers.get(container_id=id)
            while running_container.status == "created":
                current_app.logger.info(f"Waiting for container to start: {running_container.status}")
                running_container = docker_client.containers.get(container_id=id)

            current_app.logger.info(f"Running container: {container}")

            user_active_bot_record = redis_interface.get_item(
                redis_value_type=RedisValueTypes.ACTIVE_BOTS, subkey=user_id
            )
            if user_active_bot_record is None:
                user_active_bot_record = {}

            user_data = data['user_env']
            store_user_config = {}
            for key in user_data.keys():
                if key not in exclude_user_fields:
                    new_key = key.replace('<USER-', '').replace('>', '')
                    store_user_config[new_key] = user_data[key]

            user_active_bot_record[id] = {}
            user_active_bot_record[id]['user_config'] = store_user_config
            user_active_bot_record[id]['status'] = running_container.status
            user_active_bot_record[id]['created_at'] = datetime.now().timestamp()

            set_item = redis_interface.set_item(
                redis_value_type=RedisValueTypes.ACTIVE_BOTS,
                subkey=user_id,
                value=user_active_bot_record
            )
            if not set_item:
                current_app.logger.info(f"Error setting active bot record for user: {user_id}")
                flask.abort(500, "Error setting active bot record for user")
        except Exception as e:
            current_app.logger.info(f"Error deploying bot: {e}")
            abort(500, "Error deploying bot")

        return {"data": {"active": user_active_bot_record, "message": "Bot deployed successfully"}}

    @token_required
    @document_login_required
    @bot_blueprint.response(status_code=200, schema=BaseResponseSchema)
    def get(self, current_user):
        """
        Get all ACTIVE bots
        """
        user_id = current_user
        docker_client: DockerClient = current_app.extensions['docker_client']
        redis_interface: RedisInterface = current_app.extensions['redis_interface']

        user_active_bot_record = redis_interface.get_item(
            redis_value_type=RedisValueTypes.ACTIVE_BOTS,
            subkey=user_id
        )
        if user_active_bot_record is None:
            user_active_bot_record = {}

        return {"data": {'active': user_active_bot_record, 'count': len(user_active_bot_record.keys())}}
