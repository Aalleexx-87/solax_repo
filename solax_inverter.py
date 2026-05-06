import asyncio
import json
import requests
import paho.mqtt.client as mqtt
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


# -----------------------
# CONFIG
# -----------------------
with open("/data/options.json") as f:
    config = json.load(f)

broker = config.get("ip_broker")
port = int(config.get("port_broker"))
username = config.get("username")
password = config.get("password")

topic = "solax/inverter_data"

TOKEN = config.get("solax_token")
SN = config.get("solax_sn")


# -----------------------
# SOLAX CLOUD API
# -----------------------
def get_data():
    url = "https://www.solaxcloud.com:9443/proxy/api/getRealtimeInfo.do"

    params = {
        "tokenId": TOKEN,
        "sn": SN
    }

    r = requests.get(url, params=params, timeout=15)
    data = r.json()

    # gestione errore API
    if isinstance(data, dict) and data.get("success") is False:
        raise Exception(data)

    return data


# -----------------------
# MQTT
# -----------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log("MQTT connesso")
    else:
        log(f"MQTT errore: {rc}")


def send_mqtt(client, data):
    payload = json.dumps(data)
    client.publish(topic, payload)
    log("MQTT inviato")


# -----------------------
# MAIN LOOP
# -----------------------
async def main():

    log("🚀 SOLAX CLOUD MODE AVVIATO (STABILE)")

    client = mqtt.Client()

    if username and password:
        client.username_pw_set(username, password)

    client.on_connect = on_connect
    client.connect(broker, port, 60)
    client.loop_start()

    while True:
        try:
            data = get_data()

            log("📡 dati ricevuti da Solax Cloud")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            send_mqtt(client, data)

        except Exception as e:
            log(f"❌ errore: {e}")

        await asyncio.sleep(60)


asyncio.run(main())
