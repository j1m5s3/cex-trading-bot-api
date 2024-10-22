from marshmallow import Schema, fields, validate, post_load

class GETLiveRatesRequestSchema(Schema):
    """
    Schema for GET /live-rates
    """

    chain_name = fields.String(required=True)
    token_symbol = fields.String(required=False)