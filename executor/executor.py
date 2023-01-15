import paho.mqtt.client as mqtt
import requests
import json

MQTT_BROKER = "127.0.0.1" 
MQTT_PORT = 1883 

def on_publish(client,userdata,result):             
    print("data published \n")
    pass

response_planned_path = requests.get('/planned_path')

client = mqtt.Client()  
client.on_publish = on_publish                          
client.connect(MQTT_BROKER,MQTT_PORT)                                
client.publish('warehouse/robot/planned_path', json.dumps(response_planned_path))    
client.loop_forever()