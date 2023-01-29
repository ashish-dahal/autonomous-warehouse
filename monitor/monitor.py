import time
import requests
import json
import paho.mqtt.client as mqtt

MQTT_BROKER = "127.0.0.1" 
MQTT_PORT = 1883 
MQTT_TOPIC = [("warehouse/map",0),("warehouse/robot/position",0), ("warehouse/package/insert",0)]

class Monitor:
    def __init__(self, MQTT_BROKER, MQTT_PORT):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        # Connect to the mqtt broker
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.subscribe(MQTT_TOPIC)
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            global Connected
            Connected = True
        else:
            print("Connection failed")

    def on_message(self, client, userdata, message):
        data = message.payload
        receive = data.decode("utf-8")
        msg = json.loads(receive)
        if message.topic == "warehouse/map":
            requests.post(url = "knowledge/map_info", data = msg)
        elif message.topic == "warehouse/robot/position":
            requests.post(url = "knowledge/robot_info", data = msg)
        elif message.topic == "warehouse/package/insert":
            requests.post(url = "knowledge/package_info", data = msg)
            
if __name__ == "__main__":
    monitor = Monitor(MQTT_BROKER, MQTT_PORT)
    monitor.client.loop_start()
    while True:
        time.sleep(1)
