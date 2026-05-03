import os


def try_parse(type, value: str):
    try:
        return type(value)
    except Exception:
        return None


# MQTT config
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST") or "mqtt"
MQTT_BROKER_PORT = try_parse(int, os.environ.get("MQTT_BROKER_PORT")) or 1883
MQTT_TOPIC = os.environ.get("MQTT_TOPIC") or "agent"

# Delay for sending data to mqtt in seconds
DELAY = try_parse(float, os.environ.get("DELAY")) or 1

# Agent data
USER_ID = try_parse(int, os.environ.get("USER_ID")) or 1
AGENT_TYPE = os.environ.get("AGENT_TYPE") or "car" # "car" | "parking_space" | "traffic_light"
LATITUDE = try_parse(float, os.environ.get("LATITUDE")) or None # None -> Car
LONTITUDE = try_parse(float, os.environ.get("LONTITUDE")) or None # None -> Car
