import asyncio
import json
import os
import paho.mqtt.client as mqtt
from datetime import datetime

from solax import RealTimeAPI, X3HybridG4, X3V34, X3

# 📁 file dove salvare il modello corretto
MODEL_FILE = "/data/solax_model.json"

# 🕒 logger con timestamp
def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# 🔐 config Home Assistant
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


# -----------------------------
# 🔍 VALIDAZIONE DATI INVERTER
# -----------------------------
def is_valid(data):
    try:
        if isinstance(data, list):
            data = data[0]

        temp = data.get("Inverter Temperature", 0)
        pv = data.get("Total PV Power", 0)

        # regole semplici ma efficaci
        if temp < -10 or temp > 120:
            return False
        if pv < 0 or pv > 20000:
            return False

        return True

    except:
        return False


# -----------------------------
# 🤖 MODELLI DA TESTARE
# -----------------------------
MODELS = [
    ("X3HybridG4", X3HybridG4),
    ("X3V34", X3V34),
    ("X3", X3),
]


# -----------------------------
# 💾 CARICA MODELLO SALVATO
# -----------------------------
def load_saved_model():
    if os.path.exists(MODEL_FILE):
        try:
            with open(MODEL_FILE) as f:
                return json.load(f).get("model")
        except:
            return None
    return None


# -----------------------------
# 💾 SALVA MODELLO SCELTO
# -----------------------------
def save_model(name):
    with open(MODEL_FILE, "w") as f:
        json.dump({"model": name}, f)


# -----------------------------
# 🔧 CREA INVERTER
# -----------------------------
def create_inverter(model_name):
    for name, cls in MODELS:
        if name == model_name:
            log(f"🔧 Uso modello: {name}")
            return cls(ip_inverter, port_inverter, password_inverter)
    return None


# -----------------------------
# 🤖 AUTO-DETECT
# -----------------------------
async def autodetect():
    log("🔍 Avvio auto-detect inverter...")

    for name, cls in MODELS:
        try:
            log(f"➡️ Test modello {name}")
            inverter = cls(ip_inverter, port_inverter, password_inverter)
            api = RealTimeAPI(inverter)

            data = await api.get_data()

            if is_valid(data):
                log(f"✅ Modello valido trovato: {name}")
                save_model(name)
                return inverter

            log(f"⚠️ Modello {name} scartato (dati non validi)")

        except Exception as e:
            log(f"❌ Errore su {name}: {e}")

    raise Exception("Nessun modello valido trovato")


# -----------------------------
# 📤 MQTT
# -----------------------------
def send_mqtt(client, data):
    payload = json.dumps(data)

    log("📦 Invio MQTT")
    print(payload)

    result = client.publish(topic, payload)
    result.wait_for_publish()

    if result.rc == 0:
        log("✅ MQTT OK")
    else:
        log(f"❌ MQTT errore: {result.rc}")


# -----------------------------
# 🚀 MAIN LOOP
# -----------------------------
async def main():

    saved = load_saved_model()

    if saved:
        log(f"📂 Modello salvato trovato: {saved}")
        inverter = create_inverter(saved)
        rt_api = RealTimeAPI(inverter)
    else:
        inverter = await autodetect()
        rt_api = RealTimeAPI(inverter)

    client = mqtt.Client()

    if username and password:
        client.username_pw_set(username, password)

    client.connect(broker, port, 60)
    client.loop_start()

    log("🔌 MQTT connesso")

    while True:
        try:
            data = await rt_api.get_data()

            if not is_valid(data):
                log("⚠️ Dati non validi, skip ciclo")
                await asyncio.sleep(60)
                continue

            log("📡 Dati inverter ricevuti")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            send_mqtt(client, data)

        except Exception as e:
            log(f"❌ Errore ciclo: {e}")

        await asyncio.sleep(60)


# -----------------------------
# START
# -----------------------------
asyncio.run(main())
