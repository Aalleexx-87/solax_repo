import asyncio
import json
import paho.mqtt.client as mqtt
from solax import discover, RealTimeAPI

# 🔐 Legge configurazioni da /data/options.json (inserite da Home Assistant)
with open("/data/options.json") as f:
    config = json.load(f)

broker = "192.168.10.17"
port = 1883
topic = "solax/inverter_data"
username = config.get("username")
password = config.get("password")

# Callback per connessione MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connesso al broker MQTT con successo")
    else:
        print(f"❌ Connessione fallita con codice: {rc}")

# Invio dati MQTT
def send_mqtt(client, data):
    try:
        payload = json.dumps(data)
        print("📦 Payload inviato su MQTT:")
        print(payload)

        result = client.publish(topic, payload)
        result.wait_for_publish()

        if result.rc == 0:
            print(f"✅ Dati pubblicati su MQTT: {topic}")
        else:
            print(f"❌ Errore nella pubblicazione: rc={result.rc}")
    except Exception as e:
        print(f"❌ Errore MQTT: {e}")

# Loop principale asincrono
async def main_loop():
    try:
        inverter = await discover("192.168.10.105", 80, pwd="605302")
        rt_api = RealTimeAPI(inverter)

        client = mqtt.Client()
        if username and password:
            client.username_pw_set(username, password)
        client.on_connect = on_connect

        print(f"🔌 Connessione a {broker}:{port}")
        client.connect(broker, port, 60)
        client.loop_start()

        while True:
            try:
                data = await rt_api.get_data()
                print("📡 Dati dall'inverter:")
                print(json.dumps(data, indent=2, ensure_ascii=False))

                send_mqtt(client, data)
            except Exception as e:
                print(f"❌ Errore dati/publishing: {e}")

            await asyncio.sleep(60)
    except Exception as e:
        print(f"❌ Errore nella scoperta dell'inverter: {e}")

# Avvio
asyncio.run(main_loop())















