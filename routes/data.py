import os
import json
import pandas as pd
import datetime as dt
from datetime import timedelta
from typing import List

from flask import current_app, make_response, jsonify, abort
from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

from external_apis.etherscan_api_interface import EtherscanAPIInterface

from db.mongo_interface import MongoInterface
from db.redis_interface import RedisInterface
from db.queries.rates import get_rates_query
from db.queries.models.rates_models import RatesIdentQueryModel

from routes.schemas.base import BaseResponseSchema
from routes.schemas.data import GETLiveRatesRequestSchema, GETHistoricalRatesRequestSchema, GETTransactionsRequestSchema
from routes.utils.data_utils import (
    create_nested_data,
    get_timestamp_range_from_option,
    create_redis_token_protocol_patterns
)

from utils.enums import RedisValueTypes
from utils.constants import ZERO_ADDRESS

data_blueprint = Blueprint(
    'data',
    __name__,
    url_prefix='/data',
    description='Data API'
)

@data_blueprint.route('/rates/live')
class LiveRatesView(MethodView):

    @data_blueprint.arguments(schema=GETLiveRatesRequestSchema, location='query')
    @data_blueprint.response(status_code=200, schema=BaseResponseSchema)
    def get(self, args):
        """
        Get live rates
        """
        redis_interface: RedisInterface = current_app.extensions['redis_interface']

        chain: str = args.get('chain_name').upper()
        protocols: list = json.loads(args.get('protocols', ['[]'])[0])
        tokens: list = json.loads(args.get('token_symbols', ['[]'])[0])

        key_patterns: list = create_redis_token_protocol_patterns(chain=chain, tokens=tokens, protocols=protocols)

        keys_found = []
        for key_pattern in key_patterns:
            keys_found.extend(list(redis_interface.scan_iter(match=key_pattern)))

        if len(keys_found) == 0:
            return {"data": {"rates": []}}

        rates_records = []
        for key in keys_found:
            data: dict = json.loads(redis_interface.get(key))
            rates_records.append(data)

        return {"data": {"rates": rates_records}}

@data_blueprint.route('/rates/history')
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
        #timestamps: list = rates_pd['timestamp'].unique().tolist()
        timestamps: list = ((pd.to_datetime(rates_pd['timestamp'], unit='s'
                               ).dt.round('min').unique() - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')).tolist()

        nested_rates: dict = create_nested_data(
            data=rates_pd,
            nest_level_0='protocol',
            nest_level_1='token_symbol',
            nested_values=['supply_apy', 'supply_apr', 'timestamp']
        )

        return {"data": {"rates": nested_rates, "timestamps": timestamps}}

@data_blueprint.route('/txns/history')
class HistoryTxnsView(MethodView):

    @data_blueprint.arguments(schema=GETTransactionsRequestSchema, location='query')
    @data_blueprint.response(status_code=200, schema=BaseResponseSchema)
    def get(self, args):
        """
        Get history transactions
        """
        etherscan_api: EtherscanAPIInterface = current_app.extensions['etherscan_api_interface']

        chainid: int = args.get('chainid')
        address: str = args.get('address')
        contract_address: str = args.get('contract_address')
        timestamp: int = args.get('timestamp')
        start_block: int = args.get('start_block')

        transfer_txns: List[dict] = etherscan_api.get_erc20_transfer_events(
            address=address,
            contract_address=contract_address,
            chainid=chainid,
            start_block=start_block,
        )
        transfer_txns_df: pd.DataFrame = pd.DataFrame(transfer_txns)
        transfer_txns_df['type'] = 'TRANSFER'

        zero_addr_idx = transfer_txns_df[transfer_txns_df['from'] == ZERO_ADDRESS]
        if zero_addr_idx.sum() > 0:
            transfer_txns_df.loc[zero_addr_idx.index, 'type'] = 'INVEST'

        transfer_txns_df.rename(
            columns={
                'contractAddress': 'token_address',
                'value': 'amount',
                'tokenSymbol': 'token_symbol',
                'timeStamp': 'timestamp',
            },
            inplace=True
        )

        desired_columns = [
            'hash', 'from', 'to', 'token_address', 'amount', 'token_symbol', 'timestamp', 'type'
        ]
        transfer_txns_df = transfer_txns_df[desired_columns]

        txn_list: list = transfer_txns_df.to_dict(orient='records')
        response_data = {
            "transactions": txn_list
        }

        return {"data": response_data}