from dataclasses import dataclass


@dataclass
class TrafficLight:
    latitude: float
    longitude: float
    traffic_volume: int
    avg_vehicle_speed: float
    accident_reported: int
    signal_status: str
