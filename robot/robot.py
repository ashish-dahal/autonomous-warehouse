import paho.mqtt.client as mqtt
import json
import time
import configparser

config = configparser.ConfigParser()
config.read('warehouse.conf')

MQTT_BROKER = config.get("mqtt_broker", "broker_name")
MQTT_PORT = config.getint("mqtt_broker", "port")


class Robot:
    def __init__(self):

        # initial state of the robot - idle
        self.state = "IDLE"

        self.position = [10, 10]

        self.assigned_package = None

        self.planned_path = []

        self.prev_path = []

    # Callback function for when a message is received on the subscribed topic.
    def on_message(self, client, userdata, msg):
        if msg.topic == "warehouse/robot/planned_path":

            print("\n", msg.topic, msg.payload)
            # Extract the JSON file from the message payload
            path_data = json.loads(msg.payload)

            '''
            Dictionary format of data as follows...

            data = {
                "package_id": "value",
                "planned_path": [(x1, y1), (x2, y2), (x3, y3), ...]
                    }

            '''

            # Initialize the robot's position and state
            self.assigned_package = path_data["package_id"]

            # check if there is no path
            if not path_data["planned_path"]:
                self.state = "NO_PATH"
                self.planned_path = []
            else:
                self.planned_path = path_data["planned_path"]

        if msg.topic == "warehouse/reset":
            self.state = "IDLE"
            self.position = [10, 10]
            self.assigned_package = None
            self.planned_path = []
            self.prev_path = []
            time.sleep(1)
            self.publish_status()

    # function to check if path has been changed
    def path_changed(self):
        while True:
            if self.prev_path != self.planned_path:
                print("\nPath has been updated")
                self.prev_path = self.planned_path
                self.move()

    def move(self):
        for point in self.planned_path:
            if self.prev_path != self.planned_path:
                print("\nPath has been updated - while moving")
                self.prev_path = self.planned_path
                self.move()
                return
            self.state = "DELIVERED" if point == self.planned_path[-1] else "DELIVERING"
            self.position = point
            print("\nRobot is now at position: ", self.position)
            self.publish_status()

    def publish_status(self):
        data_send = {
            "state": self.state,
            "position": self.position,
            "assignedPackage": self.assigned_package
        }

        print("\n", data_send)

        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT)
        client.loop_start()
        time.sleep(0.5)
        # Publish the JSON file to the broker on a specific topic
        client.publish("warehouse/robot/status", json.dumps(data_send))
        client.loop_stop()

    # Callback function for when the client receives a CONNACK response from the server.

    def on_connect(self, client, userdata, flags, rc):
        print("\nConnected with result code " + str(rc))

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection.")
        elif rc == 0:
            print("Disconnected successfully.")

    def start(self):
        self.client = mqtt.Client()
        # Assign the callback functions
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Connect to the MQTT broker
        self.client.connect(MQTT_BROKER, MQTT_PORT)

        # Publish the initial status of the robot
        self.publish_status()

        # Subscribe to the topic to receive planned path
        self.client.subscribe("warehouse/robot/planned_path")
        self.client.subscribe("warehouse/reset")
        self.client.loop_start()
        # Check continuously if path has been changed
        self.path_changed()
        self.client.loop_stop()


if __name__ == "__main__":
    robot = Robot()
    robot.start()
