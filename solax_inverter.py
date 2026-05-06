import asyncio
import json
import requests
import paho.mqtt.client as mqtt
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


# CONFIG
with open("/data/options.json") as f:
    config = json.load(f)

broker = config["ip_broker"]
port = int(config["port_broker"])

username = config.get("username", "")
password = config.get("password", "")

TOKEN = config["solax_token"]
SN = config["solax_sn"]

topic = "solax/inverter_data"


# SOLAX CLOUD
def get_data():
    url = "https://www.solaxcloud.com:9443/proxy/api/getRealtimeInfo.do"

    r = requests.get(url, params={"tokenId": TOKEN, "sn": SN}, timeout=15)
    return r.json()


# MQTT
def send(client, data):
    client.publish(topic, json.dumps(data))
    log("MQTT inviato")


def on_connect(client, userdata, flags, rc):
    log("MQTT OK" if rc == 0 else f"MQTT error {rc}")


async def main():

    log("🚀 AVVIO SOLAX CLOUD (VERSIONE STABILE)")

    client = mqtt.Client()

    if username and password:
        client.username_pw_set(username, password)

    client.on_connect = on_connect
    client.connect(broker, port, 60)
    client.loop_start()

    while True:
        try:
            data = get_data()

            log("📡 dati ricevuti")
            print(json.dumps(data, indent=2))

            send(client, data)

        except Exception as e:
            log(f"❌ errore: {e}")

        await asyncio.sleep(60)


asyncio.run(main())
