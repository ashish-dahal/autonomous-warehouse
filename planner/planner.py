from heapq import heappush, heappop
from math import sqrt
import paho.mqtt.client as mqtt
import time
import random


class Planner:
    def __init__(self, broker_name, broker_port):
        self.map = []
        self.source = ()
        self.destination = ()
        self.path = []  # The path will be stored here
        self.client = mqtt.Client()

        # Connect to the mqtt broker
        # self. client.connect(broker_name, broker_port)

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

    # The callback for when the client receives a CONNACK response from the server.

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe("analyzer/command")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print(msg.topic+": \n"+str(msg.payload))

    def start(self):
        """Starts the planner.
        """
        # The callback for when a PUBLISH message is received from the server.
        self.client.on_connect = self.on_connect

        # The callback for when a PUBLISH message is received from the server.
        self.client.on_message = self.on_message


if __name__ == "__main__":
    # generate random 10*10 map
    map = [[random.randint(0, 1) for _ in range(20)] for _ in range(20)]
    # generate random source and destinatiion based on the map
    source = (random.randint(0, 19), random.randint(0, 19))
    destination = (random.randint(0, 19), random.randint(0, 19))

    map[source[0]][source[1]] = 0
    map[destination[0]][destination[1]] = 0

    print("\nMap:")
    for m in map:
        print(m)

    print("Source: ", source)
    print("Destination: ", destination)
    print("-"*10)

    planner = Planner("mqtt_broker", 1883)
    path = planner.a_star(map, source, destination)

    print("Update map with path (Indicated by '2'):")
    if path is not None:
        # print the line on path in map
        for p in path:
            map[p[0]][p[1]] = 2

        for m in map:
            print(m)

        print("path: ", path)
    else:
        print("Path doesn't exist")
