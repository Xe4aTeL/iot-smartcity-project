from pydantic import BaseModel
from app.entities.agent_data import AgentData


class ProcessedAgentData(BaseModel):
    agent_data: AgentData
    # Car
    road_state: str # "bump" | "pit" | "flat"

    # Traffic Light
    traffic_jam: bool # "True" | "False"

    # Parking Space
    possible_theft: bool # "True" | "False" | if a car is sitting on spot and ENL is high -> possible theft
