from dataclasses import dataclass

from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.gyroscope import Gyroscope


@dataclass
class AggregatedData:
    accelerometer: Accelerometer
    gps: Gps
    gyroscope: Gyroscope
    timestamp: datetime
    user_id: int
