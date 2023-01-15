import time
import json
import paho.mqtt.client as mqtt

MQTT_BROKER = "127.0.0.1" #change later
MQTT_PORT = 1234 #change later
MQTT_TOPIC = [("warehouse/map",0),("warehouse/robot/position",0), ("warehouse/package/insert",0)]


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected
        Connected = True
    else:
        print("Connection failed")

def on_message(client, userdata, message):
    data = message.payload
    receive=data.decode("utf-8")
    m_decode = json.loads(receive)
    print ("Message received: "  + str(m_decode))


Connected = False   #global variable - connection state

client = mqtt.Client("Python")
client.on_connect= on_connect
client.on_message= on_message
client.connect(MQTT_BROKER,MQTT_PORT)

client.loop_start()

while Connected != True:
    time.sleep(0.1)

client.subscribe(MQTT_TOPIC)

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("exiting")

