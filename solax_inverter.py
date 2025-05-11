import asyncio
import json
import paho.mqtt.client as mqtt
from solax import discover, RealTimeAPI

# Configura il broker MQTT
broker = "192.168.10.17"
port = 1883
topic = "solax/inverter_data"
username = "mqtt_user"
password = "25081987Aa?"

# Callback per connessione MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connesso al broker MQTT con successo")
    else:
        print(f"❌ Connessione fallita con codice: {rc}")

# Funzione per inviare i dati al broker MQTT
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
            print(f"❌ Errore nella pubblicazione sul topic {topic}: rc={result.rc}")
    except Exception as e:
        print(f"❌ Errore durante la pubblicazione MQTT: {e}")

# Funzione asincrona principale in loop
async def main_loop():
    try:
        inverter = await discover("192.168.10.105", 80, pwd="605302")
        rt_api = RealTimeAPI(inverter)

        # Creiamo il client MQTT una volta sola e lo teniamo attivo
        client = mqtt.Client()
        client.username_pw_set(username, password)
        client.on_connect = on_connect

        print(f"🔌 Mi connetto al broker MQTT su {broker}:{port}")
        client.connect(broker, port, 60)
        client.loop_start()

        while True:
            try:
                data = await rt_api.get_data()
                print("📡 Dati ricevuti dall'inverter:")
                print(json.dumps(data, indent=2, ensure_ascii=False))

                send_mqtt(client, data)
            except Exception as e:
                print(f"❌ Errore durante la lettura/publishing: {e}")

            await asyncio.sleep(60)  # ⏱ Attende 60 secondi prima della prossima lettura

    except Exception as e:
        print(f"❌ Errore durante la scoperta dell'inverter: {e}")

# Avvia il loop
asyncio.run(main_loop())














