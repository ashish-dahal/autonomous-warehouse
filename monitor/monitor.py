import requests
import paho.mqtt.client as mqtt
import configparser

config = configparser.ConfigParser()
config.read('warehouse.conf')

MQTT_BROKER = config.get("mqtt_broker", "broker_name")
MQTT_PORT = config.getint("mqtt_broker", "port")
HOST = config.get("knowledge", "host")
MQTT_TOPICS = [("warehouse/map", 0), ("warehouse/robot/status",
                                      0), ("warehouse/package/insert", 0), ("warehouse/reset", 0)]


class Monitor:
    def __init__(self):
        self.client = mqtt.Client()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker.")
        else:
            print("Connection failed.")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, message):
        msg = message.payload
        if message.topic == "warehouse/map":
            self.insert_map_info(msg)
            print("Map info inserted")
        elif message.topic == "warehouse/robot/status":
            self.insert_robot_info(msg)
            print("Robot info inserted")
        elif message.topic == "warehouse/package/insert":
            self.insert_package_info(msg)
            print("Package info inserted")
        elif message.topic == "warehouse/reset":
            self.reset_knowledge()
            print("Knowledge reset")

        self.command_analyzer()

    # Send command to analyzer to start analyzing
    def command_analyzer(self):
        self.client.publish("warehouse/monitor/command", "start")
        print("Commanded Analyzer to start analyzing")

    # Insert map info into knowledge

    def insert_map_info(self, map_info):
        requests.post(url=f"{HOST}/map_info", data=map_info)
        print(map_info)

    # Insert robot info into knowledge
    def insert_robot_info(self, robot_info):
        requests.post(url=f"{HOST}/robot_info", data=robot_info)
        print(robot_info)

    # Insert package info into knowledge
    def insert_package_info(self, package_info):
        requests.post(url=f"{HOST}/package_info",
                      data=package_info)
        print(package_info)

    # Reset knowledge
    def reset_knowledge(self):
        requests.post(url=f"{HOST}/reset")
    # Start the monitor

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        # Connect to the mqtt broker
        self.client.subscribe(MQTT_TOPICS)
        self.client.loop_forever()


if __name__ == "__main__":
    monitor = Monitor()
    monitor.start()
