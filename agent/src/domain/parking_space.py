from dataclasses import dataclass


@dataclass
class ParkingSpace:
    latitude: float
    longitude: float
    occupancy_status: str
    environmental_noise_level: float
