from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData


def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, Gyroscope and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    road_state: str = "flat"
    traffic_jam = False
    possible_theft = False

    if agent_data.agent_type == "car":
        if agent_data.accelerometer.y > 8000:
            road_state: str = "bump"
        elif agent_data.accelerometer.y < -10500:
            road_state: str = "pit"

    if agent_data.agent_type == "traffic_light" and agent_data.traffic_light.avg_vehicle_speed < 30:
        traffic_jam = True

    if agent_data.agent_type == "parking_space" and agent_data.parking_space.occupancy_status == "Occupied" and agent_data.parking_space.environmental_noise_level > 70:
        possible_theft = True

    processed_data_batch: ProcessedAgentData = ProcessedAgentData(
        road_state=road_state,
        traffic_jam=traffic_jam,
        possible_theft=possible_theft,
        agent_data=agent_data
        )

    return processed_data_batch
