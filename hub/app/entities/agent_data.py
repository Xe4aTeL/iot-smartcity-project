from datetime import datetime
from pydantic import BaseModel, field_validator


class AccelerometerData(BaseModel):
    x: int
    y: int
    z: int


class GpsData(BaseModel):
    longitude: float
    latitude: float


class GyroscopeData(BaseModel):
    roll: float
    pitch: float
    yaw: float


class ParkingSpaceData(BaseModel):
    latitude: float
    longitude: float
    occupancy_status: str
    environmental_noise_level: float


class TrafficLightData(BaseModel):
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

    accelerometer: AccelerometerData | None
    gps: GpsData | None
    gyroscope: GyroscopeData | None
    traffic_light: TrafficLightData | None
    parking_space: ParkingSpaceData | None

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )