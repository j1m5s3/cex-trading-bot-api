from utils.enums import ChainIds as c_ids
from marshmallow import Schema, fields, validate, post_load

class GETLiveRatesRequestSchema(Schema):
    """
    Schema for GET /live-rates
    """

    chain_name = fields.String(required=True)
    token_symbol = fields.String(required=False)


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