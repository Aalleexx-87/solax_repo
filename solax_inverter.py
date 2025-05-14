import asyncio
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import paho.mqtt.client as mqtt
from solax import discover, RealTimeAPI

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
        print("✅ Connesso al broker MQTT con successo")
    else:
        print(f"❌ Connessione al broker MQTT fallita con codice: {rc}")

# Pubblica dati su MQTT
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
        print(f"❌ Errore durante l'invio MQTT: {e}")

# Loop principale asincrono
async def main_loop():
    try:
        print(f"🔍 Scoperta inverter su {ip_inverter}:{port_inverter}")
        inverter = await discover(ip_inverter, port_inverter, pwd=password_inverter)
        print(f"✅ Inverter scoperto: {inverter}")
        rt_api = RealTimeAPI(inverter)

        client = mqtt.Client(protocol=mqtt.MQTTv311)  # ✅ Specifica protocollo per evitare warning
        client.enable_logger()  # 🔍 Abilita log dettagliati su stdout
        if username and password:
            client.username_pw_set(username, password)
        client.on_connect = on_connect

        print(f"🔌 Connessione a broker MQTT {broker}:{port}")
        client.connect(broker, port, 60)
        client.loop_start()

        # 📡 Testa una pubblicazione iniziale
        client.publish("solax/test", "✅ Add-on avviato correttamente")

        # 🧪 Test lettura iniziale
        print("⏳ Test lettura dati...")
        raw_data = await rt_api.get_data()
        print("✅ Lettura dati riuscita!")
        print(json.dumps(dict(raw_data), indent=2))

        # 🔁 Ciclo continuo ogni 60 secondi
        while True:
            try:
                print("⏳ Chiedo dati all'inverter...")
                raw_data = await rt_api.get_data()
                data = dict(raw_data)

                # ⏱ Aggiunta timestamp con fuso orario Roma
                try:
                    timestamp = datetime.now(ZoneInfo("Europe/Rome")).isoformat()
                except Exception as tz_err:
                    print(f"⚠️ Errore nel calcolo del timestamp: {tz_err}")
                    timestamp = datetime.now().isoformat()

                data["timestamp"] = timestamp

                print(f"🕒 Timestamp aggiunto: {timestamp}")
                print("📡 Dati completi da inviare:")
                print(json.dumps(data, indent=2, ensure_ascii=False))

                send_mqtt(client, data)

            except Exception as e:
                print(f"❌ Errore nella lettura dati o pubblicazione MQTT: {e}")

            await asyncio.sleep(60)

    except Exception as e:
        print(f"❌ Errore nella connessione all'inverter: {e}")

# Avvio script
asyncio.run(main_loop())
