from ast import literal_eval
import base64
import json
import mosquitto
import sys

if len(sys.argv) != 5:
    print("Usage: {} <AppEUI> <password> <DevEUI> <message>".format(sys.argv[0]))
    sys.exit(1)

appeui = sys.argv[1]
password = sys.argv[2]
deveui = sys.argv[3]
msg = literal_eval('b"' + sys.argv[4] + '"')
client = mosquitto.Mosquitto()
client.username_pw_set(appeui, password)
client.connect("staging.thethingsnetwork.org")
payload = json.dumps(dict(payload=base64.b64encode(msg).decode(), port=1, ttl="1h"))
client.publish("{}/devices/{}/down".format(appeui, deveui), payload)
