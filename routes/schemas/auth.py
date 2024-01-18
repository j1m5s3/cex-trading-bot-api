from marshmallow import Schema, fields, validate


class AuthRequestSchema(Schema):
    """
    Schema for POST request to /auth
    """
    username = fields.String(required=True)
    password = fields.String(required=True)


class SignUpRequestSchema(Schema):
    """
    Schema for POST request to /auth
    """
    username = fields.String(required=True)
    password = fields.String(required=True)
    email = fields.Email(validate=validate.Email(error='Not a valid email address'))
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
