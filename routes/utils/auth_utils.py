import jwt
from functools import wraps
from copy import deepcopy
from flask import request, jsonify, make_response, current_app, abort

from db.mongo_interface import MongoInterface


def document_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)

    decorated._apidoc = deepcopy(getattr(f, "_apidoc", {}))
    decorated._apidoc.setdefault('manual_doc', {})
    decorated._apidoc['manual_doc']['security'] = [{"Bearer Auth": []}]

    return decorated


# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # ensure the jwt-token is passed with the headers
        mongo_interface: MongoInterface = current_app.extensions['mongo_interface']
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:  # throw error if no token provided
            return abort(401, "Token is missing!")
        try:
            # decode the token to obtain user public_id
            token = token.split(' ')[1]
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = mongo_interface.find_one(
                collection='users',
                query={'username': data['sub']}
            )
            if not current_user:
                abort(401, "Invalid token!")
        except:
            abort(401, "Invalid token!")
        # Return the user information attached to the token
        return f(current_user=current_user['username'], *args, **kwargs)

    return decorator
