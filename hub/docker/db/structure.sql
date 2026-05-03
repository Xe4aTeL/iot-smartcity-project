CREATE TABLE processed_agent_data (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    road_state VARCHAR(255) NOT NULL,
    traffic_jam VARCHAR(255) NOT NULL,
    possible_theft VARCHAR(255) NOT NULL,
    -- Pos
    latitude FLOAT,
    longitude FLOAT,
    -- Car
    x INTEGER,
    y INTEGER,
    z INTEGER,
    roll FLOAT,
    pitch FLOAT,
    yaw FLOAT,
    -- Traffic Lights
    traffic_volume INTEGER,
    avg_vehicle_speed FLOAT,
    accident_reported INTEGER,
    signal_status VARCHAR(255),
    -- Parking Space
    occupancy_status VARCHAR(255),
    environmental_noise_level FLOAT
);