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
    if agent_data.accelerometer.y > 8000:
        road_state: str = "bump"
    elif agent_data.accelerometer.y < -10500:
        road_state: str = "pit"
    else:
        road_state: str = "flat"
    processed_data_batch: ProcessedAgentData = ProcessedAgentData(road_state=road_state, agent_data=agent_data)

    return processed_data_batch
