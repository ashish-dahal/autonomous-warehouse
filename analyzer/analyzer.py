def has_obstacle_in_path(grid, path):
    # get the dimensions of the grid
    rows, cols = len(grid), len(grid[0])

    # iterate through the path and check if any point in the path lies on an obstacle
    for x, y in path:
        # check if the coordinates are valid (i.e., within the bounds of the grid)
        if x < 0 or x >= rows or y < 0 or y >= cols:
            return True  # invalid coordinates, return True

        # check if there is an obstacle at the current point in the path
        if grid[x][y] == 1:
            return True  # obstacle found, return True

    # no obstacle found in the path
    return False
