import serial
import json
import time
import paho.mqtt.client as mqtt

PORT = "/dev/ttyACM0"
BAUD = 9600

client = mqtt.Client()
client.connect("localhost", 1883, 60)

ser = serial.Serial(PORT, BAUD, timeout=2)
time.sleep(2)

print("Pont Série -> MQTT démarré...")

while True:
    try:
        line = ser.readline().decode("utf-8").strip()
        if not line:
            continue
        data = json.loads(line)

        if "temperature" in data:
            client.publish("/temperature", str(data["temperature"]))
        if "humidite" in data:
            client.publish("/humidite", str(data["humidite"]))
        if "pression" in data:
            client.publish("/pression", str(data["pression"]))

        print("Publié :", data)

    except json.JSONDecodeError:
        pass
    except Exception as e:
        print("Erreur :", e)
        time.sleep(1)
