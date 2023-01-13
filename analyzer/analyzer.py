from typing import List, Tuple


class Analyzer:
    def __init__(self, map: List[List[int]], knowledge):
        self.map = map
        self.knowledge = knowledge

    def detect_obstacles(self):
        """ Detects new obstacles in the map. """
        # Iterate over the map and check for obstacles
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if self.map[i][j] == 1:
                    # Check if this obstacle was already known
                    if (i, j) not in self.knowledge.obstacles:
                        # If not, add it to the list of known obstacles
                        self.knowledge.obstacles.append((i, j))
                        # Update the knowledge database with the new obstacle
                        self.knowledge.update_database((i, j), "obstacle")

    def assign_package(self, package: Tuple[Tuple[int, int], Tuple[int, int], int]):
        """ Assigns a package to a robot based on its priority. """
        # Sort the list of available packages by priority
        sorted_packages = sorted(self.knowledge.packages, key=lambda x: x[2], reverse=True)
        # Assign the package with the highest priority to a robot
        self.knowledge.assign_package(sorted_packages[0][0])

    def get_highest_priority_package(self):
        """ Returns the ID of the package with the highest priority. """
        # Sort the list of available packages by priority
        sorted_packages = sorted(self.knowledge.packages, key=lambda x: x[2], reverse=True)
        # Return the ID of the package with the highest priority
        return sorted_packages[0][0]