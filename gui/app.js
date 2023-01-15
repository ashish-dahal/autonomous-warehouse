////////////////////////////////////////////////////////////////////////////////////////////
// Utility functions


function createControlBox(grid, robot, packages) {
    // Create a div to hold the floating box
    const floatingBox = document.createElement("div");
    floatingBox.id = "floating-box";
    document.body.appendChild(floatingBox);

    // Create a button to reset the grid
    const resetButton = document.createElement("button");
    resetButton.id = "reset-button";
    resetButton.innerHTML = "Reset";
    resetButton.addEventListener("click", () => { resetGrid(grid, robot, packages) });
    floatingBox.appendChild(resetButton);

}

// function to handle mouse events
function handleMouseEvent(event) {
    const x = event.target.dataset.x;
    const y = event.target.dataset.y;

    event.target.classList.toggle("animate");

    // Check if the clicked cell already has an obstacle
    if (grid.grid[x][y] === 1) {
        // If it does, remove the obstacle
        grid.removeObstacle(x, y);
        event.target.classList.remove("obstacle");
    } else {
        // If it doesn't have package or robot, add an obstacle
        if (grid.grid[x][y] !== 2 && grid.grid[x][y] !== 3) {
            grid.addObstacle(x, y);
            event.target.classList.add("obstacle");
        }
    }

    // Publish the grid to the mqtt broker
    grid.publish(client);
}

// function to handle mouse down event
function handleMouseDown(event) {
    handleMouseEvent(event);
}


// function to handle mouse enter event
function handleMouseEnter(event) {
    if (event.buttons === 1) {
        handleMouseEvent(event);
    }
}

// function to reset the grid
function resetGrid(grid, robot, packages) {
    // reset the grid
    grid.reset();

    // reset the robot
    robot.reset();

    // reset the packages
    packages.reset();

    // Get all the grid cells
    const gridCells = document.getElementsByClassName("grid-cell");

    // Remove the obstacle class from all the grid cells
    for (let i = 0; i < gridCells.length; i++) {
        gridCells[i].classList.remove("obstacle");
    }
}

// // function to publish the grid
// function publishGrid(grid) {
//     // Publish the grid to the mqtt broker
//     grid.publish();
// }

//////////////////////////////////////////////////////////////////////////////////////////////////////
// Classes


// Create a class to represent a grid
class Grid {
    constructor(rowSize, colSize, client) {
        this.rowSize = rowSize;
        this.colSize = colSize;

        // Initialize a 2D array to store the grid cells
        this.grid = new Array(rowSize).fill(0).map(() => new Array(colSize).fill(0));
        this.displayGrid();
        this.client = client;
    }

    // Method to add an obstacle at a given cell
    addObstacle(x, y) {
        // Update the grid to show an obstacle at the given cell
        this.grid[x][y] = 1;
    }

    // Method to remove an obstacle at a given cell
    removeObstacle(x, y) {
        // Update the grid to show no obstacle at the given cell
        this.grid[x][y] = 0;
    }

    // reset the grid
    reset() {
        this.grid = new Array(this.rowSize).fill(0).map(() => new Array(this.colSize).fill(0));
        this.publish();
    }

    // publish the grid to the mqtt broker
    publish() {
        this.client.publish('warehouse/map', JSON.stringify(this.grid));
    }

    // Method to display the grid
    displayGrid() {
        // create the grid container element
        const gridContainer = document.createElement("div");
        gridContainer.id = "grid";

        // Add the grid container to the body of the page
        document.body.appendChild(gridContainer);

        // Set the grid container's dimensions
        gridContainer.style.gridTemplateColumns = `repeat(${this.grid[0].length}, 40px)`;
        gridContainer.style.gridTemplateRows = `repeat(${this.grid.length}, 40px)`;

        // Create the grid cells and add them to the container
        for (let i = 0; i < this.grid.length; i++) {
            for (let j = 0; j < this.grid[i].length; j++) {
                // Create a new div element to represent a grid cell
                const cell = document.createElement("div");

                // Set the x and y coordinates of the cell as data attributes
                cell.dataset.x = i;
                cell.dataset.y = j;

                // Add the "grid-cell" class to the cell
                cell.classList.add("grid-cell");

                // Add event listeners for click and drag events
                cell.addEventListener("mousedown", handleMouseDown);
                cell.addEventListener("mouseenter", handleMouseEnter)

                // Add the cell to the grid container
                gridContainer.appendChild(cell);

                cell.addEventListener("dragover", function (event) {
                    event.preventDefault();
                });

                cell.addEventListener("drop", function (event) {
                    event.preventDefault();
                    const packageId = event.dataTransfer.getData("text");
                    event.target.appendChild(document.getElementById(packageId));
                });
            }
        }
    }
}

class Packages {
    constructor(client) {
        this.packages = [];
        this.client = client;
    }

    addPackage(id, source, destination) {
        grid.grid[this.position[0]][this.position[1]] = 3;
        let newPackage = { id: id, source: source, destination: destination };
        this.packages.push(newPackage);
        this.publish(newPackage, 'warehouse/package/add');
    }

    removePackage(id) {
        grid.grid[this.position[0]][this.position[1]] = 0;
        let removedPackage = this.packages.find(pack => pack.id === id);
        this.packages = this.packages.filter(pack => pack.id !== id);
        this.publish(removedPackage.id, 'warehouse/package/remove');
    }

    publish(id, topic) {
        this.client.publish(topic, JSON.stringify(id));
    }

    reset() {
        this.packages = [];
    }

    displayPackages() {
        for (let i = 0; i < this.packages.length; i++) {
            let packageImg = document.createElement('div');
            packageImg.classList.add('packageImg');
            packageImg.id = this.packageImgs[i].id;
            packageImg.draggable = true;
            packageImg.addEventListener('dragstart', function (event) {
                event.dataTransfer.setData("text", event.target.id);
            });
            document.getElementById('grid').appendChild(packageImg);
        }
    }

}

class Robot {
    constructor(client) {
        this.position = [10, 10];
        this.state = "IDLE";
        this.assignedPackage = null;
        this.client = client;

        // create robot element from artifacts/robot.png
        this.robot = document.createElement('img');
        this.robot.src = './artifacts/robot_fetching.png';
        this.robot.classList.add('robot');
        this.robot.dataset.x = this.position[0];
        this.robot.dataset.y = this.position[1];
        document.getElementById('grid').appendChild(this.robot);
        this.displayRobot()

        // create mqtt client
        this.client.subscribe('warehouse/robot/state');


    }

    // update robot position
    updatePosition(x, y) {
        grid.grid[this.position[0]][this.position[1]] = 0;
        this.position = [x, y];
        grid.grid[this.position[0]][this.position[1]] = 2;
        this.displayRobot();

    }

    updateState(state) {
        this.position = state.position;
        this.state = state.state;
        this.assignedPackage = state.assignedPackage;
    }

    subscribe() {
        this.client.on('message', (topic, message) => {
            let state = JSON.parse(message);
            this.updateState(state);
        });
    }

    publish() {
        this.client.publish('warehouse/robot/position', JSON.stringify(this));
    }

    reset() {
        this.position = [10, 10];
        grid.grid[this.position[0]][this.position[1]] = 2;
        this.state = "IDLE";
        this.assignedPackage = null;
        this.displayRobot();
    }

    displayRobot() {
        // create robot element
        this.robot.style.gridRowStart = this.position[0] + 1;
        this.robot.style.gridColumnStart = this.position[1] + 1;
    }
}



////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//APP STARTS HERE

// Connect to mqtt broker
const client = mqtt.connect('ws://localhost:8000/mqtt');

client.on('connect', () => {
    console.log('Connected to MQTT Broker');
});

client.on('message', (topic, message) => {
    console.log(topic, message.toString());
});

// Create a new Grid object
const grid = new Grid(23, 37, client);

// Create a new Packages object
const packages = new Packages(client);
packages.addPackage(1, [0, 0], [10, 10]);
packages.addPackage(2, [0, 0], [10, 10]);
packages.addPackage(3, [0, 0], [10, 10]);

// Create a new Robot object
const robot = new Robot(client);

// Create the control box
createControlBox(grid, robot, packages);

// publish the grid
grid.publish()
