from marshmallow import fields
from marshmallow import Schema
from marshmallow import validate


def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    created = fields.DateTime(dump_only=True)
    name = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=50)]
    )
    location = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=50)]
    )
    description = fields.Str(
        required=True,
        validate=[validate.Length(min=5, max=200)]
    )


class AuthSchema(Schema):
    id = fields.Int(dump_only=True)
    created = fields.DateTime(dump_only=True)
    username = fields.Str(required=True, validate=must_not_be_blank)
    email = fields.Str(
        required=True,
        validate=validate.Email(error='Not a valid email address')
    )
    role = fields.Int(dump_only=True)
    token = fields.Str(
        required=True,
        validate=[validate.Length(min=50, max=50)]
    )
