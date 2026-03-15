from marshmallow import Schema, fields
from schema.accelerometer_schema import AccelerometerSchema
from schema.gps_schema import GpsSchema
from schema.gyroscope_schema import GyroscopeSchema


class AggregatedDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    gyroscope = fields.Nested(GyroscopeSchema)
    timestamp = fields.DateTime("iso")
    user_id = fields.Int()
