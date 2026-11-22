import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

URL = "http://localhost:8086"
ORG = "iot"
BUCKET = "mesures"
TOKEN = open("/home/ammoun/secrets/influx-token").read().strip()
TOPICS = {"/temperature": "temperature", "/humidite": "humidite", "/pression": "pression"}

influx = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = influx.write_api(write_options=SYNCHRONOUS)

def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected to MQTT")
    for topic in TOPICS:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    name = TOPICS.get(msg.topic)
    if name is None:
        return
    try:
        value = float(msg.payload.decode())
    except ValueError:
        return
    try:
        point = Point("environnement").tag("capteur", "nano33-ble-sense").field(name, value)
        write_api.write(bucket=BUCKET, record=point)
        print(name, value)
    except Exception as e:
        print("InfluxDB error:", e)

try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)   # paho 2.x
except AttributeError:
    client = mqtt.Client()                                    # paho 1.x
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()
