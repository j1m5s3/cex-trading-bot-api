import os
import json
from datetime import datetime

from flask import current_app, make_response, jsonify, abort
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from db.mongo_interface import MongoInterface
from db.redis_interface import RedisInterface

from routes.schemas.base import BaseResponseSchema
from routes.schemas.data import GETLiveRatesRequestSchema


from utils.enums import RedisValueTypes

data_blueprint = Blueprint(
    'data',
    __name__,
    url_prefix='/data/rates',
    description='Data API'
)

@data_blueprint.route('/live')
class LiveRatesView(MethodView):

    @data_blueprint.arguments(schema=GETLiveRatesRequestSchema, location='query')
    @data_blueprint.response(status_code=200, schema=BaseResponseSchema)
    def get(self, args):
        """
        Get live rates
        """
        redis_interface: RedisInterface = current_app.extensions['redis_interface']

        chain: str = args.get('chain_name').upper()
        token: str = args.get('token_symbol', None)

        pattern = f"{chain}*"
        if token:
            pattern = f"{pattern}*{token.upper()}*RATES"

        keys_found = list(redis_interface.scan_iter(match=pattern))
        if len(keys_found) == 0:
            return {"data": {"rates": []}}

        rates_records = []
        for key in keys_found:
            data: dict = json.loads(redis_interface.get(key))
            rates_records.append(data)

        return {"data": {"rates": rates_records}}

@data_blueprint.route('/history')
class HistoryRatesView(MethodView):

    @jwt_required
    @data_blueprint.response(status_code=200, schema=BaseResponseSchema)
    def get(self):
        """
        Get history rates
        """
        # TODO: Implement query params

        mongo_interface: MongoInterface = current_app.extensions['mongo_interface']
        data = mongo_interface.get_data()
        return make_response(jsonify(data), 200)