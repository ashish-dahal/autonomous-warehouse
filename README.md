### To run the warehouse application:

1. From the root of the project, run `docker-compose build`
1. Run `docker-compose up`
1. From the browser, go to `localhost:8080`


### Instructions for usage:
1. Obstacles can be inserted/removed by clicking and dragging on the map
2. Packages can be added with `Add package` button
3. Refresh the page to restart
4. The robot starts operating only after adding packages.
5. The green box represents the destination of the current package


### Known bugs and limitations:

The app satisfies the defined requirements, however there are some known bugs and limitations as follows that is needed to be kept in mind while running the application:

1. The obstacles can only be inserted when the robot has not picked up the package.
2. Additional packages cannot be inserted while the robot has not completed delivering the packages.
3. Using the reset button causes robot to replicate, use the browser refresh button instead.
4. Docker container needs to be re-run if any other runtime bugs appear