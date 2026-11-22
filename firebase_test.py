import firebase_admin
from firebase_admin import credentials, db

# 1. Load the key: the identity of your Pi
cred = credentials.Certificate("/home/ammoun/secrets/firebase-key.json")

# 2. Connect, giving the exact address of the Belgium database
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://iot-node-arduino-raspberry-default-rtdb.europe-west1.firebasedatabase.app"
})

# 3. Write "hello" at the path /test
db.reference("test").set("hello")
print("Written to Firebase")
