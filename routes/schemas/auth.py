from marshmallow import Schema, fields, validate


class AuthRequestSchema(Schema):
    """
    Schema for POST request to /auth
    """
    username = fields.String(required=True)
    password = fields.String(required=True)
