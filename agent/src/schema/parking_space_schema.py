from marshmallow import Schema, fields


class ParkingSpaceSchema(Schema):
    latitude = fields.Number()
    longitude = fields.Number()
    occupancy_status = fields.String()
    environmental_noise_level = fields.Number()
