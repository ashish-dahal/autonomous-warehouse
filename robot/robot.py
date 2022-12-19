import paho.mqtt.client as mqtt

'''

This code creates an MQTT client that subscribes to the topic "robot/path" to receive the planned path as an array of tuples. 
When a message is received, the planned path is extracted and iterated over to move the robot along the path. 
The robot's current position and state are updated and published to the MQTT broker in real time. 
The function move_robot simulates the movement of the robot by printing a message.
'''

# Initialize the robot's position and state
position = (0, 0)
state = "idle"

# Define the MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code:", rc)
    # Subscribe to the topic for receiving the planned path
    client.subscribe("robot/path")

def on_message(client, userdata, msg):
    global position, state
    # Parse the message and extract the planned path
    path = eval(msg.payload)
    # Set the state to "executing"
    state = "executing"
    # Iterate over the planned path and move the robot
    for p in path:
        # Update the position
        position = p
        # Publish the updated position and state to the MQTT broker
        client.publish("robot/position", str(position))
        client.publish("robot/state", state)
        # Simulate the movement of the robot
        move_robot(p)
    # Set the state to "idle"
    state = "idle"
    # Publish the updated state to the MQTT broker
    client.publish("robot/state", state)

# Define a function to simulate the movement of the robot
def move_robot(destination):
    # Simulate the movement of the robot by printing a message
    print(f"Moving to {destination}...")

# Initialize the MQTT client and set the callback functions
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect("localhost", 1883, 60)

# Start the MQTT client loop to process incoming messages
client.loop_forever()