from marshmallow import Schema, fields


class ContestSchema(Schema):
    id = fields.Int()
    is_active = fields.Bool()


class GetContestSchema(Schema):
    is_active = fields.Bool()


class ResponseGetContestSchema(Schema):
    data = fields.Nested(ContestSchema(), many=True)


class SetContestStatusSchema(Schema):
    chat_id = fields.Int()
    is_active = fields.Bool()


class ResponseContestSchema(Schema):
    chat_id = fields.Int(attribute="id")


class DeleteMembersSchema(Schema):
    chat_id = fields.Int()
