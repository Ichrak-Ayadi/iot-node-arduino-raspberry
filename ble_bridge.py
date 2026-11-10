import asyncio
import struct
import paho.mqtt.client as mqtt
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "IoT-Node-Sense"
CHARS = {
    "19b10001-e8f2-537e-4f6c-d104768a1214": "/temperature",
    "19b10002-e8f2-537e-4f6c-d104768a1214": "/humidite",
    "19b10003-e8f2-537e-4f6c-d104768a1214": "/pression",
}

try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # paho 2.x
except AttributeError:
    client = mqtt.Client()                                   # paho 1.x
client.connect("localhost", 1883, 60)
client.loop_start()   # gere la reconnexion MQTT en arriere-plan

def make_handler(topic):
    def handler(_, data):
        value = struct.unpack("<f", data)[0]
        client.publish(topic, f"{value:.2f}")
        print(topic, round(value, 2))
    return handler

async def run_once():
    print("Recherche de l'Arduino en BLE...")
    device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=15)
    if device is None:
        print("Arduino introuvable.")
        return

    lost = asyncio.Event()
    async with BleakClient(device, disconnected_callback=lambda _: lost.set()) as ble:
        print("Connecte a", device.address)
        for uuid, topic in CHARS.items():
            await ble.start_notify(uuid, make_handler(topic))
        await lost.wait()   # attend une deconnexion
    print("Connexion BLE perdue.")

async def main():
    while True:
        try:
            await run_once()
        except Exception as e:
            print("Erreur BLE :", e)
        await asyncio.sleep(3)   # puis on retente

asyncio.run(main())
