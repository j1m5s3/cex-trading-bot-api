from datetime import datetime

from flask import current_app, abort
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import create_access_token

from db.mongo_interface import MongoInterface
from routes.schemas.base import BaseResponseSchema
from routes.schemas.auth import AuthRequestSchema, SignUpRequestSchema

auth_blueprint = Blueprint(
    'login',
    __name__,
    url_prefix='',
    description='Login to get JWT token'
)


@auth_blueprint.route('/login')
class Login(MethodView):

    @auth_blueprint.arguments(AuthRequestSchema, location='json')
    @auth_blueprint.response(status_code=200, schema=BaseResponseSchema)
    def post(self, data):
        """
        Login
        """
        mongo_interface: MongoInterface = current_app.extensions['mongo_interface']

        username = data['username']
        password = data['password']

        user = mongo_interface.find_one(
            collection='users',
            query={'username': username, 'password': password}
        )

        if user is None:
            current_app.logger.info('User not found')
            abort(401, message='User not found')

        access_token = create_access_token(identity=username)
        return {
            'status': 'success',
            'data': {
                'timestamp': datetime.now(),
                'access_token': access_token
            }
        }


@auth_blueprint.route('/signup')
class SignUp(MethodView):

        @auth_blueprint.arguments(SignUpRequestSchema, location='json')
        @auth_blueprint.response(status_code=200, schema=BaseResponseSchema)
        def post(self, data):
            """
            Signup
            """
            mongo_interface: MongoInterface = current_app.extensions['mongo_interface']

            username = data['username']
            password = data['password']
            email = data['email']
            first_name = data['first_name']
            last_name = data['last_name']

            user = mongo_interface.find_one(
                collection='users',
                query={'username': username}
            )

            if user is not None:
                current_app.logger.info('User already exists')
                abort(401, message='User already exists')

            mongo_interface.insert(
                collection='users',
                document={
                    'username': username,
                    'password': password,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )

            return {
                'status': 'success',
                'data': {
                    'timestamp': datetime.now(),
                    'username': username
                }
            }