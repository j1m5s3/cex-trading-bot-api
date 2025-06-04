from utils.enums import ChainIds as c_ids
from marshmallow import Schema, fields, validate, post_load

class GETLiveRatesRequestSchema(Schema):
    """
    Schema for GET /live-rates
    """

    chain_name = fields.String(required=True)
    token_symbols = fields.List(fields.String(), required=False)
    protocols = fields.List(fields.String(), required=False)


class GETHistoricalRatesRequestSchema(Schema):
    """
    Schema for GET /historical-rates
    """

    chain_name = fields.String(required=True, validate=validate.OneOf(
        [c_ids.ARBITRUM.name, c_ids.ETH_MAIN.name, c_ids.OPTIMISM.name]
    ))
    protocol = fields.String(required=False)
    token_address = fields.String(required=False)
    token_symbol = fields.String(required=False)
    start_ts = fields.Integer(required=False)
    end_ts = fields.Integer(required=False)
    time_range_option = fields.String(required=False, validate=validate.OneOf(
        ["1D", "1W", "1M"]
    ))

class GETTransactionsRequestSchema(Schema):
    """
    Schema for GET /transactions
    """

    chain_id = fields.Integer(required=True, validate=validate.OneOf(
        [c_ids.ARBITRUM.value, c_ids.ETH_MAIN.value, c_ids.OPTIMISM.value, c_ids.ETH_SEPOLIA.value]
    ))
    address = fields.String(required=True)
    contract_address = fields.String(required=False, default='')
    page = fields.Integer(required=False, default=1)
    timestamp = fields.Integer(required=True)
    start_block = fields.Integer(required=False, default=0)
    end_block = fields.Integer(required=False, default=99999999)
    closest = fields.String(required=False, validate=validate.OneOf(["before", "after"]), default="before")
    sort = fields.String(required=False, validate=validate.OneOf(["asc", "desc"]), default="asc")