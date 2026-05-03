from datetime import datetime
from pydantic import BaseModel, field_validator


class Accelerometer(BaseModel):
    x: int
    y: int
    z: int


class Gps(BaseModel):
    longitude: float
    latitude: float


class Gyroscope(BaseModel):
    roll: float
    pitch: float
    yaw: float


class ParkingSpace(BaseModel):
    latitude: float
    longitude: float
    occupancy_status: str
    environmental_noise_level: float


class TrafficLight(BaseModel):
    latitude: float
    longitude: float
    traffic_volume: int
    avg_vehicle_speed: float
    accident_reported: int
    signal_status: str


class AgentData(BaseModel):
    user_id: int
    agent_type: str
    timestamp: datetime

    accelerometer: Accelerometer | None
    gps: Gps | None
    gyroscope: Gyroscope | None
    traffic_light: TrafficLight | None
    parking_space: ParkingSpace | None
    
    @classmethod
    @field_validator("timestamp", mode="before")
    def parse_timestamp(cls, value):
        # Convert the timestamp to a datetime object
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )