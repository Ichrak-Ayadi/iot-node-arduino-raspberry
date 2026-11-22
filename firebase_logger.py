import time
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, db

KEY_PATH = "/home/ammoun/secrets/firebase-key.json"
DB_URL = "https://iot-node-arduino-raspberry-default-rtdb.europe-west1.firebasedatabase.app"
TOPICS = {"/temperature": "temperature", "/humidite": "humidite", "/pression": "pression"}
INTERVAL = 5

firebase_admin.initialize_app(credentials.Certificate(KEY_PATH), {"databaseURL": DB_URL})
last_write = {}

def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected to MQTT")
    for topic in TOPICS:
        client.subscribe(topic)          # re-subscribes after any reconnection

def on_message(client, userdata, msg):
    name = TOPICS.get(msg.topic)
    if name is None:
        return
    now = time.time()
    if now - last_write.get(name, 0) < INTERVAL:
        return                           # too soon, skip this value
    try:
        value = float(msg.payload.decode())
    except ValueError:
        return
    last_write[name] = now
    stamp = datetime.now(timezone.utc).isoformat()
    try:
        db.reference(f"mesures/{name}").push({"valeur": value, "horodatage": stamp})
        print(name, value, stamp)
    except Exception as e:
        print("Firebase error:", e)

try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)   # paho 2.x
except AttributeError:
    client = mqtt.Client()                                    # paho 1.x
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()
