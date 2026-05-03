from marshmallow import Schema, fields
from schema.accelerometer_schema import AccelerometerSchema
from schema.gps_schema import GpsSchema
from schema.gyroscope_schema import GyroscopeSchema
from schema.traffic_light_schema import TrafficLightSchema
from schema.parking_space_schema import ParkingSpaceSchema


class AggregatedDataSchema(Schema):
    user_id = fields.Integer()
    agent_type = fields.String()
    timestamp = fields.DateTime("iso")

    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    gyroscope = fields.Nested(GyroscopeSchema)

    traffic_light = fields.Nested(TrafficLightSchema)
    
    parking_space = fields.Nested(ParkingSpaceSchema)
