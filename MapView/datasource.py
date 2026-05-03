import asyncio
import json
import websockets
from datetime import datetime
from typing import Optional
from kivy import Logger
from pydantic import BaseModel, field_validator
from config import STORE_HOST, STORE_PORT


# Pydantic models
class ProcessedAgentData(BaseModel):
    agent_type: str  # e.g., 'car', 'traffic_light', 'parking_space'
    user_id: int
    timestamp: datetime
    latitude: float
    longitude: float
    
    # Optional fields depending on the agent
    road_state: Optional[str] = None
    traffic_jam: Optional[bool] = False
    possible_theft: Optional[bool] = False
    x: Optional[int] = None
    y: Optional[int] = None
    z: Optional[int] = None
    roll: Optional[float] = None
    pitch: Optional[float] = None
    yaw: Optional[float] = None
    traffic_volume: Optional[int] = None
    avg_vehicle_speed: Optional[float] = None
    accident_reported: Optional[int] = None
    signal_status: Optional[str] = None
    occupancy_status: Optional[str] = None
    environmental_noise_level: Optional[float] = None

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


class Datasource:
    def __init__(self, user_id: int):
        self.index = 0
        self.user_id = user_id
        self.connection_status = None
        self._new_points = []
        asyncio.ensure_future(self.connect_to_server())

    def get_new_points(self):
        Logger.debug(self._new_points)
        points = self._new_points
        self._new_points = []
        return points

    async def connect_to_server(self):
        uri = f"ws://{STORE_HOST}:{STORE_PORT}/ws/{self.user_id}"
        while True:
            Logger.debug("CONNECT TO SERVER")
            async with websockets.connect(uri) as websocket:
                self.connection_status = "Connected"
                try:
                    while True:
                        data = await websocket.recv()
                        parsed_data = json.loads(data)
                        self.handle_received_data(parsed_data)
                except websockets.ConnectionClosedOK:
                    self.connection_status = "Disconnected"
                    Logger.debug("SERVER DISCONNECT")

    def handle_received_data(self, data):
        # Update your UI or perform actions with received data here
        Logger.debug(f"Received data: {data}")
        processed_agent_data_list = sorted(
            [
                ProcessedAgentData(**processed_data_json)
                for processed_data_json in json.loads(data)
            ],
            key=lambda v: v.timestamp,
        )
        self._new_points.extend(processed_agent_data_list)
