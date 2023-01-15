import paho.mqtt.client as mqtt
import json

'''
This piece of code recieves a JSON format from MQQT broker and convert to Python dictionary
'''

#initial state of the robot - idle
state="idle"

# Callback function for when a message is received on the subscribed topic.
def on_message(client, userdata, msg):
    # Extract the JSON file from the message payload
    json_file = json.loads(msg.payload)
    print("Received JSON file: ", json_file)
    # Convert the JSON file into a Python dictionary
    data = json.loads(json_file)
    print("Converted data: ", data)

    '''
    Dictionary format of data as follows...

    data = {
        "package_id": "value1", 
        "planned_path": "value2"
            }

    '''

    # Initialize the robot's position and state

    package_id = data["package_id"]
    planned_path = data["planned_path"]
    current_pos = planned_path[0]

    for point in planned_path[1:]:
        state = "delivering the package..."
        # Calculate the distance between the current position and the next point
        x_distance = point[0] - current_pos[0]
        y_distance = point[1] - current_pos[1]
        # Move the robot to the next point

        current_pos = point
        print("Robot is now at position: ", current_pos)


        data_send = {
            "package_id": package_id,
            "robot_state": state,
            "position": current_pos
                    }

        # Convert the dictionary to a JSON file
        json_data = json.dumps(data_send)

        # Publish the JSON file to the broker on a specific topic
        client.publish("warehouse/robot/status", json_data)

    # Set the state to "finished", once done
    state = "finished"

    data_send["robot_state"] = state
    json_data = json.dumps(data_send)
    # Publish the JSON file to the broker on a specific topic
    client.publish("warehouse/robot/status", json_data)


# MQTT client setup
client = mqtt.Client()
client.on_message = on_message

# Connect to the MQTT broker
client.connect("MQQT_broker", 1883)

# Subscribe to the topic to receive JSON file
client.subscribe("warehouse/robot/planned path")

'''

This code creates an MQTT client that subscribes to the topic "robot/path" to receive the planned path as an array of tuples. 
When a message is received, the planned path is extracted and iterated over to move the robot along the path. 
The robot's current position and state are updated and published to the MQTT broker in real time. 
The function move_robot simulates the movement of the robot by printing a message.

'''



client.loop_forever()