import asyncio
import json
import time
import paho.mqtt.client as mqtt
from solax import discover, RealTimeAPI

OPTIONS_FILE = "/data/options.json"
MQTT_TOPIC = "solax/inverter_data"
POLL_INTERVAL = 60  # secondi – NON scendere sotto i 30 per G4

# --------------------------------------------------
# Caricamento configurazione
# --------------------------------------------------
with open(OPTIONS_FILE) as f:
    config = json.load(f)

IP_INVERTER = config.get("ip_inverter")
PORT_INVERTER = int(config.get("port_inverter", 80))
PWD_INVERTER = config.get("password_inverter")

MQTT_BROKER = config.get("ip_broker")
MQTT_PORT = int(config.get("port_broker", 1883))
MQTT_USER = config.get("username")
MQTT_PASS = config.get("password")

# --------------------------------------------------
# MQTT
# --------------------------------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ MQTT connesso")
    else:
        print(f"❌ MQTT errore connessione rc={rc}")

def mqtt_connect():
    client = mqtt.Client()
    if MQTT_USER and MQTT_PASS:
        client.username_pw_set(MQTT_USER, MQTT_PASS)

    client.on_connect = on_connect
    client.reconnect_delay_set(min_delay=5, max_delay=60)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    return client

def publish_mqtt(client, payload):
    try:
        msg = json.dumps(payload)
        client.publish(MQTT_TOPIC, msg)
        print("📤 MQTT pubblicato")
    except Exception as e:
        print(f"❌ Errore MQTT: {e}")

# --------------------------------------------------
# Lettura inverter (G4 safe)
# --------------------------------------------------
async def read_inverter():
    inverter = await discover(
        IP_INVERTER,
        PORT_INVERTER,
        pwd=PWD_INVERTER
    )
    rt_api = RealTimeAPI(inverter)
    data = await rt_api.get_data()
    return data

# --------------------------------------------------
# Loop principale
# --------------------------------------------------
async def main():
    mqtt_client = mqtt_connect()
    print("🚀 Solax inverter loop avviato")

    while True:
        start = time.time()

        try:
            print("🔄 Connessione inverter...")
            data = await read_inverter()

            print("📡 Dati ricevuti")
            publish_mqtt(mqtt_client, data)

        except Exception as e:
            print(f"❌ Errore inverter: {e}")

        elapsed = time.time() - start
        sleep_time = max(0, POLL_INTERVAL - elapsed)

        print(f"⏳ Attesa {int(sleep_time)}s\n")
        await asyncio.sleep(sleep_time)

# --------------------------------------------------
# Avvio
# --------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())

