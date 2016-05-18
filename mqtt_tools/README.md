# MQTT Examples

These utilities uses the following parameters:

* AppEUI - Application EUI. Can be seen with command `ttnctl applications` as EUI
* password - Access key to application. Can be seen with command `ttnctl applications` as "Access Keys"
* DevEUI - Device EUI. Can be seen with command `ttnctl devices`

## Mosquitto subscribe tool

Mosquitto provides a command line tool for subscription. This can you a
raw json packet, but won't decipher the base64 payload.

    mosquitto_sub -h staging.thethingsnetwork.org -v -u <AppEUI> -P <password> -t +/devices/#

## Python Subscribe
[ttn_mqtt_sub.py]() script provides subscription of MQTT messages and
will decode the payload element: 

    python ttn_mqtt_sub.py <AppEUI> <password>

## Python publish
[ttn_mqtt_pub.py]() script encodes the message and publish a valid json
structure:

    python ttn_mqtt_pub.py <AppEUI> <password> <DevEUI> <message>

## Node-RED
For Node-RED this json structure can be imported: [ttn-node-red.json]()

You will need to go into mqtt nodes and configure them for correct
paramters.