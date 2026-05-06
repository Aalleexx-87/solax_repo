import asyncio
import json
import paho.mqtt.client as mqtt
from solax import RealTimeAPI, X3
from datetime import datetime

# 🕒 funzione log con timestamp
def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# 🔐 Legge configurazioni da /data/options.json
with open("/data/options.json") as f:
    config = json.load(f)

# Parametri MQTT
broker = config.get("ip_broker")
port = int(config.get("port_broker"))
username = config.get("username")
password = config.get("password")
topic = "solax/inverter_data"

# Parametri inverter
ip_inverter = config.get("ip_inverter")
port_inverter = int(config.get("port_inverter"))
password_inverter = config.get("password_inverter")

# Callback connessione MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log("✅ Connesso al broker MQTT con successo")
    else:
        log(f"❌ Connessione MQTT fallita con codice: {rc}")

# Pubblica dati su MQTT
def send_mqtt(client, data):
    try:
        payload = json.dumps(data)

        log("📦 Payload MQTT inviato:")
        print(payload)

        result = client.publish(topic, payload)
        result.wait_for_publish()

        if result.rc == 0:
            log(f"✅ Dati pubblicati su {topic}")
        else:
            log(f"❌ Errore pubblicazione MQTT: rc={result.rc}")

    except Exception as e:
        log(f"❌ Errore invio MQTT: {e}")

# Loop principale
async def main_loop():
    try:
        log("🔧 Avvio connessione inverter Q.VOLT HYB-G3 (X3 compat mode)")

        # 🚀 inverter FIXATO (no discover)
        inverter = X3(ip_inverter, port_inverter, password_inverter)
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
                log(f"❌ Errore ciclo lettura/pubblicazione: {e}")

            await asyncio.sleep(60)

    except Exception as e:
        log(f"❌ Errore generale: {e}")

# 🚀 start
asyncio.run(main_loop())
