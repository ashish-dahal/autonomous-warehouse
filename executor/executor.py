import paho.mqtt.client as mqtt
import requests
import configparser

config = configparser.ConfigParser()
config.read('warehouse.conf')

MQTT_BROKER = config.get("mqtt_broker", "broker_name")
MQTT_PORT = config.getint("mqtt_broker", "port")
HOST = config.get("knowledge", "host")


class Executor:
    def __init__(self):
        self.MQTT_TOPICS = [("warehouse/planner/command", 0)]
        self.client = mqtt.Client()
        self.client.connect(MQTT_BROKER, MQTT_PORT)

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
        planned_path = requests.get(f'{HOST}/planned_path').json()
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
