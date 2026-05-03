import asyncio
import json
from typing import Set, Dict, List, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from datetime import datetime
from pydantic import BaseModel, field_validator
from config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)

# FastAPI app setup
app = FastAPI()
# SQLAlchemy setup
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
# Define the ProcessedAgentData table
processed_agent_data = Table(
    "processed_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("agent_type", String),
    Column("user_id", Integer),
    Column("timestamp", DateTime),
    Column("road_state", String),
    Column("traffic_jam", Boolean),
    Column("possible_theft", Boolean),
    # Pos
    Column("latitude", Float),
    Column("longitude", Float),
    # Car
    Column("x", Integer),
    Column("y", Integer),
    Column("z", Integer),
    Column("roll", Float),
    Column("pitch", Float),
    Column("yaw", Float),
    # Traffic Light
    Column("traffic_volume", Integer),
    Column("avg_vehicle_speed", Float),
    Column("accident_reported", Integer),
    Column("signal_status", String),
    # Parking Space
    Column("occupancy_status", String),
    Column("environmental_noise_level", Float),
)
SessionLocal = sessionmaker(bind=engine)


# SQLAlchemy model
class ProcessedAgentDataInDB(BaseModel):
    id: int
    user_id: int
    timestamp: datetime
    road_state: str
    traffic_jam: bool
    possible_theft: bool
    latitude: float
    longitude: float
    x: int
    y: int
    z: int
    roll: float
    pitch: float
    yaw: float
    traffic_volume: int
    avg_vehicle_speed: float
    accident_reported: int
    signal_status: str
    occupancy_status: str
    environmental_noise_level: float


# FastAPI models
class AccelerometerData(BaseModel):
    x: int
    y: int
    z: int


class GpsData(BaseModel):
    latitude: float
    longitude: float


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


class ProcessedAgentData(BaseModel):
    agent_data: AgentData
    road_state: str
    traffic_jam: bool
    possible_theft: bool


# WebSocket subscriptions
subscriptions: Dict[int, Set[WebSocket]] = {}


# FastAPI WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in subscriptions:
        subscriptions[user_id] = set()
    subscriptions[user_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions[user_id].remove(websocket)

# Function to send data to a specific subscribed user
async def send_data_to_subscribers(user_id: int, data):
    if user_id in subscriptions:
        for websocket in subscriptions[user_id]:
            await websocket.send_json(json.dumps(data))

# # Function to send data to all subscribed users
# async def send_data_to_all_subscribers(data):
#     for websocket in subscriptions.values():
#         await websocket.send_json(json.dumps(data))


# FastAPI CRUDL endpoints


@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    # Insert data to database
    # Send data to subscribers
    to_insert = []
    for item in data:
        to_insert.append({
            "agent_type": item.agent_data.agent_type,
            "user_id": item.agent_data.user_id,
            "timestamp": str(item.agent_data.timestamp),
            "road_state": item.road_state,
            "traffic_jam": item.traffic_jam,
            "possible_theft": item.possible_theft,
            "latitude": item.agent_data.gps.latitude if item.agent_data.agent_type == "car" else \
            item.agent_data.traffic_light.latitude if item.agent_data.agent_type == "traffic_light" else \
            item.agent_data.parking_space.latitude,
            "longitude": item.agent_data.gps.longitude if item.agent_data.agent_type == "car" else \
            item.agent_data.traffic_light.longitude if item.agent_data.agent_type == "traffic_light" else \
            item.agent_data.parking_space.longitude,
            "x": item.agent_data.accelerometer.x if item.agent_data.agent_type == "car" else None,
            "y": item.agent_data.accelerometer.y if item.agent_data.agent_type == "car" else None,
            "z": item.agent_data.accelerometer.z if item.agent_data.agent_type == "car" else None,
            "roll": item.agent_data.gyroscope.roll if item.agent_data.agent_type == "car" else None,
            "pitch": item.agent_data.gyroscope.pitch if item.agent_data.agent_type == "car" else None,
            "yaw": item.agent_data.gyroscope.yaw if item.agent_data.agent_type == "car" else None,
            "traffic_volume": item.agent_data.traffic_light.traffic_volume if item.agent_data.agent_type == "traffic_light" else None,
            "avg_vehicle_speed": item.agent_data.traffic_light.avg_vehicle_speed if item.agent_data.agent_type == "traffic_light" else None,
            "accident_reported": item.agent_data.traffic_light.accident_reported if item.agent_data.agent_type == "traffic_light" else None,
            "signal_status": item.agent_data.traffic_light.signal_status if item.agent_data.agent_type == "traffic_light" else None,
            "occupancy_status": item.agent_data.parking_space.occupancy_status if item.agent_data.agent_type == "parking_space" else None,
            "environmental_noise_level": item.agent_data.parking_space.environmental_noise_level if item.agent_data.agent_type == "parking_space" else None,
        })

    db_session = SessionLocal()
    try:
        insert_stmt = processed_agent_data.insert().values(to_insert)
        db_session.execute(insert_stmt)
        db_session.commit()

        created_count = len(to_insert)
        select_stmt = (
            processed_agent_data.select()
            .order_by(processed_agent_data.c.id.desc())
            .limit(created_count)
        )
        rows = db_session.execute(select_stmt).fetchall()
        await send_data_to_subscribers(item.agent_data.user_id, to_insert)
        return str(rows)
    finally:
        db_session.close()


@app.get(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def read_processed_agent_data(processed_agent_data_id: int):
    # Get data by id
    db_session = SessionLocal()
    try:
        select_stmt = processed_agent_data.select().where(
            processed_agent_data.c.id == processed_agent_data_id
        )
        row = db_session.execute(select_stmt).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="ProcessedAgentData not found")
        return row
    finally:
        db_session.close()


@app.get("/processed_agent_data/", response_model=list[ProcessedAgentDataInDB])
def list_processed_agent_data():
    # Get list of data
    db_session = SessionLocal()
    try:
        select_stmt = processed_agent_data.select()
        rows = db_session.execute(select_stmt).fetchall()
        return rows
    finally:
        db_session.close()


@app.put(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    # Update data
    db_session = SessionLocal()
    try:
        update_stmt = (
            processed_agent_data.update()
            .where(processed_agent_data.c.id == processed_agent_data_id)
            .values(
                agent_type=data.agent_data.agent_type,
                user_id=data.agent_data.user_id,
                timestamp=data.agent_data.timestamp,
                road_state=data.road_state,
                traffic_jam=data.traffic_jam,
                possible_theft=data.possible_theft,
                latitude=data.agent_data.gps.latitude if data.agent_data.agent_type == "car" else \
                data.agent_data.traffic_light.latitude if data.agent_data.agent_type == "traffic_light" else \
                data.agent_data.parking_space.latitude,
                longitude=data.agent_data.gps.longitude if data.agent_data.agent_type == "car" else \
                data.agent_data.traffic_light.longitude if data.agent_data.agent_type == "traffic_light" else \
                data.agent_data.parking_space.longitude,
                x=data.agent_data.accelerometer.x if item.agent_data.agent_type == "car" else None,
                y=data.agent_data.accelerometer.y if item.agent_data.agent_type == "car" else None,
                z=data.agent_data.accelerometer.z if item.agent_data.agent_type == "car" else None,
                roll=data.agent_data.gyroscope.roll if item.agent_data.agent_type == "car" else None,
                pitch=data.agent_data.gyroscope.pitch if item.agent_data.agent_type == "car" else None,
                yaw=data.agent_data.gyroscope.yaw if item.agent_data.agent_type == "car" else None,
                traffic_volume=data.agent_data.traffic_light.traffic_volume if item.agent_data.agent_type == "traffic_light" else None,
                avg_vehicle_speed=data.agent_data.traffic_light.avg_vehicle_speed if item.agent_data.agent_type == "traffic_light" else None,
                accident_reported=data.agent_data.traffic_light.accident_reported if item.agent_data.agent_type == "traffic_light" else None,
                signal_status=data.agent_data.traffic_light.signal_status if item.agent_data.agent_type == "traffic_light" else None,
                occupancy_status=data.agent_data.parking_space.data.agent_data.traffic_light if item.agent_data.agent_type == "parking_space" else None,
                environmental_noise_level=data.agent_data.parking_space.data.agent_data.traffic_light if item.agent_data.agent_type == "parking_space" else None,
            )
            .returning(processed_agent_data)
        )

        updated_row = db_session.execute(update_stmt).fetchone()
        db_session.commit()

        if updated_row is None:
            raise HTTPException(
                status_code=404, detail="ProcessedAgentData to update not found"
            )

        return updated_row
    finally:
        db_session.close()


@app.delete(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def delete_processed_agent_data(processed_agent_data_id: int):
    # Delete by id
    db_session = SessionLocal()
    try:
        select_stmt = processed_agent_data.select().where(
            processed_agent_data.c.id == processed_agent_data_id
        )
        row = db_session.execute(select_stmt).fetchone()

        if row is None:
            raise HTTPException(
                status_code=404, detail="ProcessedAgentData to delete not found"
            )

        delete_stmt = processed_agent_data.delete().where(
            processed_agent_data.c.id == processed_agent_data_id
        )
        db_session.execute(delete_stmt)
        db_session.commit()

        return row
    finally:
        db_session.close()



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
