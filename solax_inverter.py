import asyncio
import json
import paho.mqtt.client as mqtt
from solax import RealTimeAPI, X3Hybrid
from datetime import datetime

# 🕒 log semplice con timestamp
def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# 🔐 Config da Home Assistant
with open("/data/options.json") as f:
    config = json.load(f)

# MQTT
broker = config.get("ip_broker")
port = int(config.get("port_broker"))
username = config.get("username")
password = config.get("password")
topic = "solax/inverter_data"

# Inverter
ip_inverter = config.get("ip_inverter")
port_inverter = int(config.get("port_inverter"))
password_inverter = config.get("password_inverter")

# -----------------------------
# MQTT callback
# -----------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log("✅ Connesso al broker MQTT")
    else:
        log(f"❌ Connessione MQTT fallita: {rc}")

# -----------------------------
# Publish MQTT
# -----------------------------
def send_mqtt(client, data):
    try:
        payload = json.dumps(data)

        log("📦 Invio MQTT payload")
        print(payload)

        result = client.publish(topic, payload)
        result.wait_for_publish()

        if result.rc == 0:
            log("✅ MQTT pubblicato correttamente")
        else:
            log(f"❌ Errore MQTT: {result.rc}")

    except Exception as e:
        log(f"❌ Errore MQTT: {e}")

# -----------------------------
# MAIN LOOP
# -----------------------------
async def main_loop():
    try:
        log(f"🔧 Connessione inverter X3Hybrid su {ip_inverter}:{port_inverter}")

        # 👉 VERSIONE STABILE (NON TOCCARE)
        inverter = X3Hybrid(ip_inverter, port_inverter, password_inverter)
        rt_api = RealTimeAPI(inverter)

        client = mqtt.Client()

        if username and password:
            client.username_pw_set(username, password)

        client.on_connect = on_connect

        log(f"🔌 Connessione MQTT {broker}:{port}")
        client.connect(broker, port, 60)
        client.loop_start()

        while True:
            try:
                data = await rt_api.get_data()

                log("📡 Dati inverter ricevuti")
                print(json.dumps(data, indent=2, ensure_ascii=False))

                send_mqtt(client, data)

            except Exception as e:
                log(f"❌ Errore ciclo: {e}")

            await asyncio.sleep(60)

    except Exception as e:
        log(f"❌ Errore iniziale: {e}")

# -----------------------------
# START
# -----------------------------
asyncio.run(main_loop())
