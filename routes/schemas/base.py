from marshmallow import Schema, fields, validate


class BaseResponseSchema(Schema):
    """
    Schema for a base response
    """
    status = fields.String(default="success")
    data = fields.Raw(required=True)
    reason = fields.String(required=False)

