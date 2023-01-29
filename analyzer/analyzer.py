import paho.mqtt.client as mqtt
import requests


class Analyzer:
    def __init__(self):
        self.map = None
        self.map_temp = None

    def get_info(self):
        # saving map to check if it was change (for example, if user added the obstacle to the map)
        self.map_temp = self.map
        # getting the map
        endpoint_map = "/map_info"
        # Send the GET request
        self.map = requests.get(endpoint_map).json()

    def check_map(self):
        if self.map_temp is None:
            return False
        # compares the two maps element by element and check if any of the elements are different
        has_changes = any(val1 != val2 for row1, row2 in zip(self.map_temp, self.map) for val1, val2 in zip(row1, row2))
        return has_changes



if __name__ == "__main__":

    analyzer = Analyzer()
    analyzer.get_info()
    changed = analyzer.check_map()

    if changed:
        client = mqtt.Client()
        # Connect to the MQTT broker
        client.connect("MQTT_broker", 1883)
        # Publish the JSON file to the broker on a specific topic
        client.publish("warehouse/analyzer/command", "Start")
        client.disconnect()
    else:
        pass
