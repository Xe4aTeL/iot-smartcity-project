from dataclasses import dataclass

from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.gyroscope import Gyroscope
from domain.traffic_light import TrafficLight
from domain.parking_space import ParkingSpace


@dataclass
class AggregatedData:
    user_id: int
    agent_type: str
    timestamp: datetime

    # Car
    accelerometer: Accelerometer
    gps: Gps
    gyroscope: Gyroscope

    # Traffic Light
    traffic_light: TrafficLight

    # Parking Space
    parking_space: ParkingSpace
