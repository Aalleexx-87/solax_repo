import asyncio
import json
import paho.mqtt.client as mqtt
from solax.inverters import X3HybridG4
import inspect

print(inspect.signature(X3HybridG4._build))
print(inspect.getsource(X3HybridG4))

with open("/data/options.json") as f:
    config = json.load(f)

broker = config.get("ip_broker")
port = int(config.get("port_broker"))
username = config.get("username")
password = config.get("password")
topic = "solax/inverter_data"
ip_inverter = config.get("ip_inverter")
port_inverter = int(config.get("port_inverter"))
password_inverter = config.get("password_inverter")

print(f"DEBUG password_inverter: '{password_inverter}'")
