### To run the warehouse application:

1. From the root of the project, run `docker-compose build`
1. Run `docker-compose up`
1. From the browser, go to `localhost:8080`


### Known bugs and limitations:

The app satisfies the requirements defined above, however there are some known bugs and limitations as follows that is needed to be kept in mind while running the application:

1. The obstacles can only be inserted when the robot has not picked up the package.
1. Additional packages cannot be inserted while the robot has not completed delivering the packages.
1. Using the reset button causes robot to replicate, use the browser refresh button instead.
1. Docker container needs to be re-run if any other runtime bugs appear