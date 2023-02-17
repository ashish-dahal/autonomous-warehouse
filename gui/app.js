////////////////////////////////////////////////////////////////////////////////////////////
// Utility functions
isFloatingBox = false;

function createControlBox(grid, robot, packages) {
    // Create a div to hold the floating box
    const floatingBox = document.createElement("div");
    floatingBox.id = "floating-box";
    document.body.appendChild(floatingBox);

    // make the box draggable acorss screen
    const draggableDiv = document.getElementById("floating-box");
    let isMouseDown = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;

    draggableDiv.addEventListener("mousedown", e => {
        isMouseDown = true;
        isFloatingBox = true;
        e.stopImmediatePropagation();
        e.preventDefault();
        initialX = e.clientX - draggableDiv.offsetLeft;
        initialY = e.clientY - draggableDiv.offsetTop;
    });

    draggableDiv.addEventListener("mouseenter", e => {
        e.stopImmediatePropagation();
        e.preventDefault();
    });

    document.addEventListener("mousemove", e => {
        e.stopImmediatePropagation();
        e.preventDefault();
        if (!isMouseDown) return;
        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;
        draggableDiv.style.left = `${currentX}px`;
        draggableDiv.style.top = `${currentY}px`;
    });

    document.addEventListener("mouseup", e => {
        isMouseDown = false;
        isFloatingBox = false;
    });



    // Create a button to reset the grid
    const resetButton = document.createElement("button");
    resetButton.id = "reset-button";
    resetButton.innerHTML = "Reset";
    resetButton.addEventListener("click", () => { resetGrid(grid, robot, packages) });
    floatingBox.appendChild(resetButton);

    // Create Add package button
    const addPackageButton = document.createElement("button");
    addPackageButton.id = "add-package-button";
    addPackageButton.innerHTML = "Add Package";
    addPackageButton.addEventListener("click", () => { addPackage(grid, packages) });
    floatingBox.appendChild(addPackageButton);
}

function addPackage(grid, packages) {
    packageNumber = packages.packages.length + 1;
    if (packageNumber > 5) {
        alert("You can't add more than 5 packages");
        return;
    }

    // generate id for the package
    packageId = `package#${packageNumber}`;

    // generate random source and see if it is not an obstacle or package or robor and if it is, generate another random source
    do {
        source = [Math.floor(Math.random() * grid.rowSize), Math.floor(Math.random() * grid.colSize)];
    } while (grid.grid[source[0]][source[1]] === 1 || grid.grid[source[0]][source[1]] === 2 || grid.grid[source[0]][source[1]] === 3 || grid.grid[source[0]][source[1]] === 4);

    // generate random destination and see if it is not an obstacle or package or robot and if it is, generate another random destination
    do {
        destination = [Math.floor(Math.random() * grid.rowSize), Math.floor(Math.random() * grid.colSize)];
    } while (grid.grid[destination[0]][destination[1]] === 1 || grid.grid[destination[0]][destination[1]] === 2 || grid.grid[destination[0]][destination[1]] === 3 || grid.grid[destination[0]][destination[1]] === 4);

    packages.addPackage(grid, packageId, source, destination);
}

// function to handle mouse events
function handleMouseEvent(event) {
    // check if the target is floating box
    if (isFloatingBox) { return; }
    const x = event.target.dataset.x;
    const y = event.target.dataset.y;

    event.target.classList.toggle("animate");

    // Check if the clicked cell already has an obstacle
    if (grid.grid[x][y] === 1) {
        // If it does, remove the obstacle
        grid.removeObstacle(x, y);
        event.target.classList.remove("obstacle");
    } else {
        // If it doesn't have package or robot, add an obstacle or package destination
        if (grid.grid[x][y] !== 2 && grid.grid[x][y] !== 3 && grid.grid[x][y] !== 4) {
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

    // publish the grid to the mqtt broker
    grid.publish();

    // Get all the grid cells
    const gridCells = document.getElementsByClassName("grid-cell");

    // Remove the obstacle class from all the grid cells
    for (let i = 0; i < gridCells.length; i++) {
        gridCells[i].classList.remove("obstacle");
    }

    // publish reset message to the mqtt broker
    client.publish('warehouse/reset', 'reset');
}

//////////////////////////////////////////////////////////////////////////////////////////////////////
// Classes


// Create a class to represent a grid
class Grid {

    constructor(rowSize, colSize, client) {
        this.rowSize = rowSize;
        this.colSize = colSize;

        // Initialize a 2D array to store the grid cells
        // 0 - empty cell
        // 1 - obstacle
        // 2 - robot
        // 3 - package
        // 4 - package destination
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
        gridContainer.style.gridTemplateColumns = `repeat(${this.grid[0].length}, 1fr)`;
        gridContainer.style.gridTemplateRows = `repeat(${this.grid.length}, 1fr)`;


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
            }
        }
    }
}

class Packages {
    constructor(client) {
        this.packages = [];
        this.client = client;
        this.current_package_id = null;
        this.prev_package_id = null;
    }

    addPackage(grid, id, source, destination) {
        grid.grid[source[0]][source[1]] = 3;
        grid.grid[destination[0]][destination[1]] = 4;
        let newPackage = { id: id, source: source, destination: destination };
        this.packages.push(newPackage);
        this.publish(newPackage, 'warehouse/package/insert');
        this.displayPackage(newPackage)
        grid.publish()
    }

    removePackage(grid, id) {
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
        let packages = document.getElementsByClassName('package');
        for (let i = packages.length - 1; i >= 0; i--) {
            packages[i].remove();
        }
        let destination = document.getElementsByClassName('destination');
        if (destination != null) {
            for (let i = destination.length - 1; i >= 0; i--) {
                destination[i].classList.remove('destination');
            }
        }
    }

    pickedUp(grid, id) {
        // remove package from grid
        let packageImg = document.getElementById(id);
        packageImg.classList.remove('package');

        // remove package from packages
        this.removePackage(grid, id);

    }

    displayPackage(pack) {
        let packageImg = document.createElement('img');
        packageImg.src = './artifacts/package.png';
        packageImg.classList.add('package');
        packageImg.id = pack.id;
        packageImg.dataset.sourceX = pack.source[0];
        packageImg.dataset.sourceY = pack.source[1];
        packageImg.dataset.destinationX = pack.destination[0];
        packageImg.dataset.destinationY = pack.destination[1];
        // packageImg.style.gridRowStart = pack.source[0] + 1;
        // packageImg.style.gridColumnStart = pack.source[1] + 1;
        // document.getElementById('grid').appendChild(packageImg);

        // get the grid cell
        document.querySelector(`[data-x="${pack.source[0]}"][data-y="${pack.source[1]}"]`).appendChild(packageImg);
    }

    // show package destination by changing background color
    displayDestination() {
        // get the grid previous cell
        let pack = this.packages.find(pack => pack.id === this.prev_package_id);
        if (typeof pack !== 'undefined') {
            let prev_cell = document.querySelector(`[data-x="${pack.destination[0]}"][data-y="${pack.destination[1]}"]`);
            prev_cell.classList.remove('destination');
        }

        // get the grid current cell
        pack = this.packages.find(pack => pack.id === this.current_package_id);
        if (typeof pack !== 'undefined') {
            let current_cell = document.querySelector(`[data-x="${pack.destination[0]}"][data-y="${pack.destination[1]}"]`);
            current_cell.classList.add('destination');
        }
        else {
            alert("No package added");
            return;
        }
    }

    // set the current package
    setCurrentPackage(id) {
        this.prev_package_id = this.current_package_id;
        this.current_package_id = id;
        this.displayDestination();
    }

    getCurrentPackage() {
        return this.packages.find(pack => pack.id === this.current_package_id);
    }
}

class Robot {
    constructor(client) {
        this.position = [10, 10];
        this.state = null;
        this.assignedPackage = null;
        this.client = client;
        this.prev_position = null;
        // create mqtt client
        this.client.subscribe('warehouse/robot/status');

        this.client.on('message', (topic, message) => {

            if (topic === 'warehouse/robot/status') {
                let status = JSON.parse(message);
                console.log(status);
                this.updateState(status);
            }
        });

        // create robot element from artifacts/robot.png
        this.robot = document.querySelector(`[data-x="10"][data-y="10"]`);
        // this.robot.src = './artifacts/robot_fetching.png';
        this.robot.classList.add('robot');
        grid.grid[10][10] = 2;
        // this.robot.dataset.x = 10;
        // this.robot.dataset.y = 10;
        // append robot to grid cell div at position [10, 10]
        // document.querySelector(`[data-x="10"][data-y="10"]`).appendChild(this.robot);
    }

    updateState(status) {
        // remove robot from previous position
        if (this.position != null) {
            this.prev_position = this.position;
            grid.grid[this.position[0]][this.position[1]] = 0;
        }

        // update robot position
        this.position = status.position;
        grid.grid[this.position[0]][this.position[1]] = 2; // 2 is robot
        this.state = status.state; // IDLE, DELIVERING, DELIVERED, NO_PATH
        // update assigned package
        this.assignedPackage = status.assignedPackage;

        this.handleStateChange();

        // update the map based on current package
        packages.setCurrentPackage(this.assignedPackage);

        // update robot position
        this.robot = document.querySelector(`[data-x="${this.position[0]}"][data-y="${this.position[1]}"]`);
        this.displayRobot();
        // grid.publish();
    }

    handleStateChange() {
        if (this.state === "NO_PATH") {
            alert("No path found for package " + this.assignedPackage + "!");
        }
        if (this.state === "DELIVERED") {
            // remove destination class of current package
            let pack = packages.getCurrentPackage();
            if (typeof pack !== 'undefined') {
                let current_cell = document.querySelector(`[data-x="${pack.destination[0]}"][data-y="${pack.destination[1]}"]`);
                current_cell.classList.remove('destination');
            }
        }
    }

    reset() {
        this.position = [10, 10];
        grid.grid[this.position[0]][this.position[1]] = 2;
        this.state = "IDLE";
        this.assignedPackage = null;
        this.displayRobot();
    }

    displayRobot() {
        // update robot image and package image
        let current_package = packages.getCurrentPackage();
        if (typeof current_package !== 'undefined') {
            if (current_package.source[0] === this.position[0] && current_package.source[1] === this.position[1]) {
                this.robot.classList.add('robot-delivering');
                // remove the package image with id from the grid cell
                let packageImg = document.getElementById(current_package.id);
                packageImg.remove();
            }
        }
        else {
            return;
        }
        // remove robot
        if (this.prev_position != null) {
            let prev_cell = document.querySelector(`div[data-x="${this.prev_position[0]}"][data-y="${this.prev_position[1]}"]`);
            // prev_cell.removeChild(prev_cell.firstChild);
            prev_cell.classList.remove('robot');
        }
        // add robot
        this.robot = document.querySelector(`div[data-x="${this.position[0]}"][data-y="${this.position[1]}"]`);
        this.robot.classList.add('robot');

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

client.publish('warehouse/reset', 'reset');

// Create a new Grid object
const grid = new Grid(23, 37, client);

// Create a new Packages object
const packages = new Packages(client);

// Create a new Robot object
const robot = new Robot(client);

// Create the control box
createControlBox(grid, robot, packages);


// publish the grid
grid.publish()
