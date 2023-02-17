import paho.mqtt.client as mqtt
import requests


class Executor:
    def __init__(self):
        self.MQTT_BROKER = "mqtt_broker"
        self.MQTT_PORT = 1883
        self.MQTT_TOPICS = [("warehouse/planner/command", 0)]
        self.HOST = "http://knowledge:5000"
        self.client = mqtt.Client()
        self.client.connect(self.MQTT_BROKER, self.MQTT_PORT)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker.")
        else:
            print("Connection failed.")

        self.client.subscribe(self.MQTT_TOPICS)

    def on_message(self, client, userdata, message):
        msg = message.payload
        if message.topic == "warehouse/planner/command":
            if msg == b"start":
                self.execute()

    def execute(self):
        planned_path = requests.get(f'{self.HOST}/planned_path').json()
        print("Publishing planned path: ", planned_path)
        self.client.publish('warehouse/robot/planned_path', planned_path)

    def start(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Starting Executor...")
        self.client.loop_forever()


if __name__ == '__main__':
    executor = Executor()
    executor.start()
