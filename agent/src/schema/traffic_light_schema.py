from marshmallow import Schema, fields


class TrafficLightSchema(Schema):
    latitude = fields.Number()
    longitude = fields.Number()
    traffic_volume = fields.Integer()
    avg_vehicle_speed = fields.Number()
    accident_reported = fields.Integer()
    signal_status = fields.String()
