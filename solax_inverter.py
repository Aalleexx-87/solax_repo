import asyncio
import json
import paho.mqtt.client as mqtt
from solax import RealTimeAPI, X3HybridG4

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
    print("MQTT OK" if rc == 0 else f"MQTT error {rc}")


def send(client, data):
    client.publish(topic, json.dumps(data))


async def main():

    print("🚀 AVVIO SOLAX LAN (STABILE)")

    inverter = X3HybridG4(ip_inverter, port_inverter, password_inverter)
    api = RealTimeAPI(inverter)

    client = mqtt.Client()

    if username and password:
        client.username_pw_set(username, password)

    client.on_connect = on_connect
    client.connect(broker, port, 60)
    client.loop_start()

    while True:
        try:
            data = await api.get_data()
            print(data)
            send(client, data)

        except Exception as e:
            print("error:", e)

        await asyncio.sleep(60)


asyncio.run(main())
