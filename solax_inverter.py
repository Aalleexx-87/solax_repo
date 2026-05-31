import asyncio
import json
import paho.mqtt.client as mqtt
# from solax import RealTimeAPI, X3Hybrid
import importlib.metadata
print(f"solax version: {importlib.metadata.version('solax')}")
import solax
print(dir(solax))
from solax import inverters
print(dir(inverters))

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

def on_connect(client, userdata, flags, rc):
    print("MQTT connected" if rc == 0 else f"MQTT error {rc}")

def send_mqtt(client, data):
    try:
        payload = json.dumps(data)
        client.publish(topic, payload).wait_for_publish()
        print("📤 MQTT sent")
    except Exception as e:
        print(f"MQTT error: {e}")

async def main():
    print(f"🔧 Connecting to inverter {ip_inverter}:{port_inverter}")
    inverter = X3Hybrid(ip_inverter, port_inverter, password_inverter)
    rt_api = RealTimeAPI(inverter)
    print(f"✅ Inverter: {inverter.__class__.__name__}")

    client = mqtt.Client()
    if username:
        client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port, 60)
    client.loop_start()

    while True:
        try:
            data = await rt_api.get_data()
            if isinstance(data, list):
                data = data[0]
            print("📡 RAW DATA:")
            print(json.dumps(data, indent=2))
            send_mqtt(client, data)
        except Exception as e:
            import traceback
            print(f"ERROR: {e}")
            traceback.print_exc()
        await asyncio.sleep(60)

asyncio.run(main())
