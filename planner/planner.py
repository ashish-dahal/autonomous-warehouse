from heapq import heappush, heappop
from math import sqrt
import paho.mqtt.client as mqtt
import requests
import json

TOPIC = "warehouse/analyzer/command"
MQTT_BROKER = "mqtt_broker"
MQTT_PORT = 1883
HOST = "http://knowledge:5000"


class Planner:
    def __init__(self, broker_name, broker_port):
        self.map = []
        self.source = ()
        self.destination = ()
        self.path = []  # The path will be stored here
        self.client = mqtt.Client()

        # Connect to the mqtt broker
        self.client.connect(broker_name, broker_port)

    def a_star(self, map, source, destination):
        """ A* algorithm to find the shortest path from the source to the destination.

        Args:
            map (list): The map of the environment.
            source (tuple): The source node.
            destination (tuple): The destination node.

        Returns:
            list: The shortest path (if exists) from the source to the destination.
            None: If there is no path from the source to the destination.

        Raises:
            ValueError: If the source or destination is an obstacle.
        """

        # Check if the source or destination is an obstacle
        if map[source[0]][source[1]] == 1:
            raise ValueError("Source is an obstacle")
        if map[destination[0]][destination[1]] == 1:
            raise ValueError("Destination is an obstacle")

        # Store the map, source, and destination
        self.map = map
        self.source = source
        self.destination = destination

        # Set up the initial map
        rows = len(self.map)  # Number of rows
        cols = len(self.map[0])  # Number of columns

        # Set up the distances map
        # Initialize all distances to infinity
        distances = [[float("inf") for _ in range(cols)] for _ in range(rows)]
        # Set the distance of the source node to 0
        distances[self.source[0]][self.source[1]] = 0

        # Set up the previous nodes map
        previous = [[None for _ in range(cols)] for _ in range(rows)]

        # Set up the priority queue with the source node as the first element
        heap = []  # The priority queue
        # Push the source node onto the priority queue
        heappush(heap, (0, self.source))

        # Main loop
        while heap:
            # Get the node with the smallest distance
            # Pop the node with the smallest distance off the priority queue
            dist, coord = heappop(heap)
            r, c = coord  # Get the row and column of the node

            # Stop if we have reached the destination
            if coord == self.destination:
                break

            # Check the four adjacent nodes
            # dr and dc are the row and column offsets of the adjacent nodea
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                next_r, next_c = r + dr, c + dc  # Get the row and column of the adjacent node

                # Check if the adjacent node is in bounds and not an obstacle
                if 0 <= next_r < rows and 0 <= next_c < cols and self.map[next_r][next_c] != 1:
                    # Update the distances and previous nodes if this path is better
                    next_dist = dist + sqrt(dr**2 + dc**2)
                    # If this path is better
                    if next_dist < distances[next_r][next_c]:
                        # Update the distance
                        distances[next_r][next_c] = next_dist
                        # Update the previous node
                        previous[next_r][next_c] = coord
                        priority = next_dist + \
                            sqrt((self.destination[0] - next_r)**2 +
                                 (self.destination[1] - next_c)**2)  # Calculate the priority of the node (distance + heuristic)
                        # Push the node onto the priority queue
                        heappush(heap, (priority, (next_r, next_c)))

        # Return the shortest path if it exists, otherwise print "no path"
        if previous[self.destination[0]][self.destination[1]] is not None:
            path = []
            coord = self.destination  # Start at the destination
            # Loop until we reach the source
            while coord is not None:
                path.append(coord)  # Add the current node to the path
                # Move to the previous node
                coord = previous[coord[0]][coord[1]]
            self.path = path[::-1]  # Reverse the path
            return self.path  # Return the path
        else:
            return None

    def get_path(self, map, robot_position, source, destination):
        """Returns the path.

        Returns:
            list: The path.
        """
        if robot_position == source:
            robot_to_source = [source]
        else:
            robot_to_source = self.a_star(map, robot_position, source)
        source_to_destination = self.a_star(map, source, destination)

        if robot_to_source is not None and source_to_destination is not None:
            return robot_to_source + source_to_destination[1:]
        else:
            return None

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe(TOPIC)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print("Message received: " + msg.topic + " " + str(msg.payload))
        if msg.topic == TOPIC:
            if msg.payload == b"start":
                # get info from knowledge

                if self.query_knowledge():
                    map_info, robot_info, package_info = self.query_knowledge()

                    # get path
                    path = self.get_path(
                        map_info, robot_info['position'], package_info['source'], package_info['destination'])

                    print("Planned path: ", path)
                    print("Update map with path (Indicated by '2'):")
                    if path is not None:
                        # insert path to knowledge in json format
                        self.insert_knowledge(json.dumps(
                            {"package_id": package_info['id'], "planned_path": path}))
                        # publish trigger to executor
                        self.client.publish(
                            "warehouse/planner/command", "start")

                        # print the line on path in map
                        for p in path:
                            map_info[p[0]][p[1]] = 2

                        for m in map_info:
                            print(m)
                    else:
                        print("Path doesn't exist")

    def query_knowledge(self):
        # get package info from rest api
        response = requests.get(
            f"{HOST}/package_info").json()

        # check if there are no packages
        if response is None:
            print("No packages inserted.")
            return False
        else:
            package_info = response

        # get map from rest api
        map = list(requests.get(f"{HOST}/map_info").json())

        # get robot info from rest api
        robot_info = requests.get(f"{HOST}/robot_info").json()

        print("\nMap:")
        for m in map:
            print(m)

        print("Robot:", robot_info['position'])
        print("Source: ", package_info['source'])
        print("Destination: ", package_info['destination'])
        print("-"*10)
        return map, robot_info, package_info

    def insert_knowledge(self, data):
        # insert path to rest api
        requests.post(f"{HOST}/planned_path", json=data)

    def start(self):
        """Starts the planner.
        """
        # The callback for when a PUBLISH message is received from the server.
        self.client.on_connect = self.on_connect

        # The callback for when a PUBLISH message is received from the server.
        self.client.on_message = self.on_message

        self.client.loop_forever()


if __name__ == "__main__":

    planner = Planner(MQTT_BROKER, MQTT_PORT)
    planner.start()
