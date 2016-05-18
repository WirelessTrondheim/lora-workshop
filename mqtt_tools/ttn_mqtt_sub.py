import base64
import json
import mosquitto
import sys

if len(sys.argv) != 3:
    print("Usage: {} <AppEUI> <password>".format(sys.argv[0]))
    sys.exit(1)

appeui = sys.argv[1]
password = sys.argv[2]

client = mosquitto.Mosquitto()
client.username_pw_set(appeui, password)


def on_connect(client, userdata, rc):
    print("Connected")
    client.subscribe("+/devices/+/up")

client.on_connect = on_connect


def on_message(client, userdata, msg):
    devid = msg.topic.split('/')[2]
    payload = base64.b64decode(json.loads(msg.payload.decode())['payload'])
    print("{}: {}".format(devid, str(payload)))

client.on_message = on_message

client.connect("staging.thethingsnetwork.org")
client.loop_forever()
