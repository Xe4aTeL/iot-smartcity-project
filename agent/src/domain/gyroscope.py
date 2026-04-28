from dataclasses import dataclass


@dataclass
class Gyroscope:
    roll: float
    pitch: float
    yaw: float
