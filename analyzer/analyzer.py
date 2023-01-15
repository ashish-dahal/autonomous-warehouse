import paho.mqtt.client as mqtt
import requests

class Analyzer:
    def __init__(self, map, package_info, robot_info ):
        self.map = map


    '''
    Function that gets data via Rest API from Knowledge component
    '''
    def get_info(self):
        # saving map to check if it was change (for example, if user added the obstacle to the map)
        map_temp = map
        # getting the map
        endpoint_map = "/map_info"
        # Send the GET request
        self.map = requests.get(endpoint_map)

        '''
        Function that checks if the map was changed, for example if the user added new obstacle to the map.
        This code compares the two maps element by element and check if any of the elements are different, 
        if it finds any difference it returns True otherwise False.
        '''
        def check_map(self):
            has_changes = any(val1 != val2 for row1, row2 in zip(map_temp, self.map) for val1, val2 in zip(row1, row2))
            return has_changes


        '''
        Function that checks if the map was changed, for example if the user added new obstacle to the map
        '''
        def check_map(self):
            has_changes = any(val1 != val2 for row1, row2 in zip(map_temp, map) for val1, val2 in zip(row1, row2))
            return has_changes

 def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))



changed = Analyzer.check_map()

if changed:
    client = mqtt.Client()
    # Connect to the MQTT broker
    client.connect("MQTT_broker", 1883)
    # Publish the JSON file to the broker on a specific topic
    client.publish("warehouse/analyzer/command", "Start")
    client.disconnect()
else:
    None



