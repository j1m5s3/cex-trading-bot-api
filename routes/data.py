import os
import json

import pandas as pd

import datetime as dt
from datetime import timedelta

from flask import current_app, make_response, jsonify, abort
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from db.mongo_interface import MongoInterface
from db.redis_interface import RedisInterface
from db.queries.rates import get_rates_query
from db.queries.models.rates_models import RatesIdentQueryModel

from routes.schemas.base import BaseResponseSchema
from routes.schemas.data import GETLiveRatesRequestSchema, GETHistoricalRatesRequestSchema
from routes.utils.data_utils import create_nested_data, get_timestamp_range_from_option

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

        if token:
            pattern = f"{chain}*{token.upper()}*RATES"
        else:
            pattern = f"{chain}*RATES"

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

    @data_blueprint.arguments(schema=GETHistoricalRatesRequestSchema, location='query')
    @data_blueprint.response(status_code=200, schema=BaseResponseSchema)
    def get(self, args):
        """
        Get history rates
        """
        mongo_interface: MongoInterface = current_app.extensions['mongo_interfaces']['on_chain']

        chain_name: str = args.get('chain_name').upper()
        protocol: str = args.get('protocol', None)
        if protocol:
            protocol = protocol.upper()
        token_address: str = args.get('token_address', None)
        token_symbol: str = args.get('token_symbol', None)
        start_ts: int = args.get('start_ts', None)
        end_ts: int = args.get('end_ts', None)
        time_range_option: str = args.get('time_range_option', None)

        if time_range_option:
            start_ts, end_ts = get_timestamp_range_from_option(time_range_option=time_range_option)

        reference_data = None
        if protocol or token_address or token_symbol:
            reference_data = RatesIdentQueryModel(protocol=protocol, token_address=token_address, token_symbol=token_symbol)

        if reference_data or (start_ts and end_ts):
            qry: dict = get_rates_query(reference_data=reference_data, start_time=start_ts, end_time=end_ts)
        else:
            qry: dict = {}

        collection_name = f"{chain_name}_RATES"
        rates_records = list(mongo_interface.find(collection=collection_name, query=qry, include_exclude={'_id': 0}))

        rates_pd: pd.DataFrame = pd.DataFrame(rates_records).sort_values(by='timestamp')
        timestamps: list = rates_pd['timestamp'].to_list()
        nested_rates: dict = create_nested_data(
            data=rates_pd,
            nest_level_0='protocol',
            nest_level_1='token_symbol',
            nested_values=['supply_apy', 'supply_apr', 'timestamp']
        )

        return {"data": {"rates": nested_rates, "timestamps": timestamps}}