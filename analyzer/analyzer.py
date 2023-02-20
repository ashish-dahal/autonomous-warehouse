import paho.mqtt.client as mqtt
import requests

import configparser

config = configparser.ConfigParser()
config.read('warehouse.conf')

MQTT_BROKER = config.get("mqtt_broker", "broker_name")
MQTT_PORT = config.getint("mqtt_broker", "port")
HOST = config.get("knowledge", "host")
TOPIC = "warehouse/monitor/command"


class Analyzer:
    def __init__(self):
        self.map = None
        self.map_temp = None
        self.client = mqtt.Client()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker.")
        else:
            print("Connection failed.")

    def on_message(self, client, userdata, message):
        msg = message.payload.decode('utf-8')
        if message.topic == TOPIC and msg == "start":
            self.analyze()

    def analyze(self):
        # analyze the map changes
        self.get_map_info()
        changed = self.check_map()
        if changed:
            # Publish the JSON file to the broker on a specific topic
            self.client.publish("warehouse/analyzer/command", "start")
            print("Map changed, commanded planner to start planning")
        else:
            print("Map did not change.")

        # analyze the robot status
        robot_info = self.get_robot_info()
        if robot_info is not None:
            if robot_info["state"] == "DELIVERED":
                # remove package from knowledge
                requests.delete(
                    url=f"{HOST}/package_info", params={"package_id": robot_info['assignedPackage']})
                print("Package delivered, removed from knowledge")
            elif robot_info["state"] == "DELIVERING":
                requests.put(
                    url=f"{HOST}/package_info", params={"package_id": robot_info['assignedPackage'], "position": robot_info['position']})
                print("Package is being delivered, updated position")

    def get_map_info(self):
        # saving map to check if it was change (for example, if user added the obstacle to the map)
        self.map_temp = self.map
        # getting the map
        endpoint_map = f"{HOST}/map_info"
        # Send the GET request
        response = requests.get(endpoint_map)
        if response.status_code == 200 and response.json() is not None:
            self.map = response.json()

    def get_robot_info(self):
        # getting the robot
        endpoint_robot = f"{HOST}/robot_info"
        # Send the GET request
        response = requests.get(endpoint_robot)
        if response.status_code == 200:
            return response.json()
        else:
            print("Status code: ", response.status_code,
                  "Error: ", response)
            return None

    def check_map(self):
        if self.map_temp is None:
            return True
        # compares the two maps element by element and check if any of the elements are different
        has_changes = any(val1 != val2 for row1, row2 in zip(
            self.map_temp, self.map) for val1, val2 in zip(row1, row2))
        return has_changes

    def start(self):
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.subscribe(TOPIC)
        self.client.loop_forever()


if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.start()
