from marshmallow import Schema, fields


class GyroscopeSchema(Schema):
    roll = fields.Number()
    pitch = fields.Number()
    yaw = fields.Number()
