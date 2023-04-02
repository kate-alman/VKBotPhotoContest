from marshmallow import Schema, fields


class AdminSchema(Schema):
    id = fields.Int(required=False)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class AdminRequestSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)
