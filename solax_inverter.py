import asyncio
import json
import paho.mqtt.client as mqtt
import requests
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# CONFIG
with open("/data/options.json") as f:
    config = json.load(f)

broker = config.get("ip_broker")
port = int(config.get("port_broker"))
username = config.get("username")
password = config.get("password")
topic = "solax/inverter_data"

ip_inverter = config.get("ip_inverter")
url = f"http://{ip_inverter}/api/realTimeData.htm"


def read_inverter():
    # chiamata DIRETTA HTTP, zero librerie Solax
    r = requests.get(url, timeout=10)
    return r.json()


def on_connect(client, userdata, flags, rc):
    log("MQTT connesso" if rc == 0 else f"MQTT errore {rc}")


def send_mqtt(client, data):
    payload = json.dumps(data)
    client.publish(topic, payload)
    log("MQTT inviato")


async def main():

    log("🚀 START DIRECT SOLAX MODE (NO AUTODETECT)")

    client = mqtt.Client()
    if username and password:
        client.username_pw_set(username, password)

    client.on_connect = on_connect
    client.connect(broker, port, 60)
    client.loop_start()

    while True:
        try:
            data = read_inverter()

            log("📡 Dati inverter OK")
            print(json.dumps(data, indent=2))

            send_mqtt(client, data)

        except Exception as e:
            log(f"❌ errore: {e}")

        await asyncio.sleep(60)


asyncio.run(main())
