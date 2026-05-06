import asyncio
import json
import paho.mqtt.client as mqtt
from datetime import datetime

# 👉 IMPORT DIRETTO (NO FACTORY / NO AUTODETECT)
from solax.inverters.x3_hybrid_g4 import X3HybridG4


# -----------------------------
# 🕒 LOG CON TIMESTAMP
# -----------------------------
def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


# -----------------------------
# 🔐 CONFIG HOME ASSISTANT
# -----------------------------
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
# 📡 MQTT CALLBACK
# -----------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        log("✅ MQTT connesso")
    else:
        log(f"❌ MQTT errore: {rc}")


# -----------------------------
# 📤 MQTT SEND
# -----------------------------
def send_mqtt(client, data):
    try:
        payload = json.dumps(data)

        log("📦 Invio MQTT")
        print(payload)

        result = client.publish(topic, payload)
        result.wait_for_publish()

        if result.rc == 0:
            log("✅ MQTT OK")
        else:
            log(f"❌ MQTT errore: {result.rc}")

    except Exception as e:
        log(f"❌ Errore MQTT: {e}")


# -----------------------------
# 🔧 LETTURA INVERTER DIRETTA
# -----------------------------
def read_inverter(inverter):
    """
    CHIAMATA DIRETTA SENZA RealTimeAPI
    (evita completamente autodetect)
    """
    return inverter.get_data()


# -----------------------------
# 🚀 MAIN LOOP
# -----------------------------
async def main():

    log("🔧 Avvio SOLAX HARD LOCK (Q.VOLT HYB-G3 3P)")

    # 👉 INVERTER BLOCCATO
    inverter = X3HybridG4(
        ip_inverter,
        port_inverter,
        password_inverter
    )

    client = mqtt.Client()

    if username and password:
        client.username_pw_set(username, password)

    client.on_connect = on_connect

    log(f"🔌 MQTT {broker}:{port}")
    client.connect(broker, port, 60)
    client.loop_start()

    while True:
        try:
            data = read_inverter(inverter)

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
