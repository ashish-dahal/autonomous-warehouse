from heapq import heappush, heappop
from math import sqrt
import paho.mqtt.client as mqtt
import time
import random


class Planner:
    def __init__(self):
        self.map = []
        self.source = ()
        self.destination = ()
        self.path = []  # The path will be stored here
        self.client = mqtt.Client()

    def __a_star(self, map, source, destination):
        self.map = map
        self.source = source
        self.destination = destination
        """ A* algorithm to find the shortest path from the source to the destination."""
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

        # Return the shortest path
        path = []
        coord = self.destination  # Start at the destination
        while coord is not None:
            path.append(coord)  # Add the current node to the path
            coord = previous[coord[0]][coord[1]]  # Move to the previous node
        self.path = path[::-1]  # Reverse the path
        return self.path

    def get_path(self, map, source, destination):
        return self.__a_star(map, source, destination)

    def publish(self, message):
        client = self.client
        client.on_connect = lambda client, userdata, flags, rc: print(
            "Connected with result code "+str(rc))
        client.on_message = lambda client, userdata, message: print(
            message.topic+" "+str(message.payload))

        client.connect("mqtt_broker", 1833, 60)
        client.publish("path", message)
        print("published")


if __name__ == "__main__":
    # generate random 10*10 map
    map = [[random.randint(0, 1) for _ in range(10)] for _ in range(10)]
    # generate random source based on the map
    source = (random.randint(0, 9), random.randint(0, 9))
    destination = (random.randint(0, 9), random.randint(0, 9))
    planner = Planner()
    path = planner.get_path(map, source, destination)
    while True:
        print(path)
        planner.publish(str(path))
        time.sleep(0.5)
