import paho.mqtt.client as mqtt
import requests
import json

class Executor:
    def __init__(self):
        self.MQTT_BROKER = "127.0.0.1" 
        self.MQTT_PORT = 1883 

    def on_publish(self, client, userdata, result):             
        print("Data published \n")
        pass

    def execute(self):
        response_planned_path = requests.get('/planned_path')

        client = mqtt.Client()  
        client.on_publish = self.on_publish                          
        client.connect(self.MQTT_BROKER, self.MQTT_PORT)                                
        client.publish('warehouse/robot/planned_path', json.dumps(response_planned_path))    
        client.loop_forever()

if name == 'main':
    executor = Executor()
    executor.execute()
