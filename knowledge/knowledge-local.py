from flask import Flask, request
import json

MAP_INFO = None
PACKAGE_INFO = []
ROBOT_INFO = None
PLANNED_PATH = None

app = Flask(__name__)

print("Knowledge is running...")


@app.route('/map_info', methods=['GET', 'POST'])
def map_info():
    if request.method == 'POST':  # insert map_info
        global MAP_INFO
        MAP_INFO = json.loads(request.data)
        print("Map info inserted:", MAP_INFO)
        # return status 200
        return "success"
    else:
        return json.dumps(MAP_INFO)


@app.route('/package_info', methods=['GET', 'POST', 'DELETE', 'PUT'])
def package_info():
    global PACKAGE_INFO
    if request.method == 'POST':  # insert package_info document
        package = json.loads(request.data)
        PACKAGE_INFO.append(package)
        print("Package info inserted:", package)
        return "success"
    elif request.method == 'GET':
        # fetch first package_info document (FIFO)
        if len(PACKAGE_INFO) != 0:
            # return first package
            package = PACKAGE_INFO[0]
        else:
            print("No package found")
            package = None
        # collection_package_info.remove(first_package_document)
        print("Get package info:", package)
        return json.dumps(package)
    elif request.method == 'DELETE':
        # delete package with given id
        package_id = request.args.get('package_id')
        for package in PACKAGE_INFO:
            if package['id'] == package_id:
                PACKAGE_INFO.remove(package)
                break
        print("Package info deleted:", package_id)
        return "success"
    elif request.method == 'PUT':
        # update package with given id and position
        package_id = request.args.get('package_id')
        position = request.args.get('position')
        if len(PACKAGE_INFO) != 0:
            for package in PACKAGE_INFO:
                if package['id'] == package_id:
                    package['position'] = (position[0], position[1])
                    break
        print("Package info updated:", package_id, position)
        return "success"


@app.route('/robot_info', methods=['GET', 'POST'])
def robot_info():
    global ROBOT_INFO
    if request.method == 'POST':  # insert robot_info
        ROBOT_INFO = json.loads(request.data)
        print("Robot info inserted:", ROBOT_INFO)
        return "success"
    elif request.method == 'GET':
        # fetch robot_info
        print("Get robot info:", ROBOT_INFO)
        return json.dumps(ROBOT_INFO)


@app.route('/planned_path', methods=['GET', 'POST'])
def planned_path():
    global PLANNED_PATH
    if request.method == 'POST':  # insert planned_path document
        PLANNED_PATH = json.loads(request.data)
        print("Planned path inserted:", PLANNED_PATH)
        return "success"
    else:  # fetch last planned_path document
        print("Get planned path:", PLANNED_PATH)
        return json.dumps(PLANNED_PATH)


# reset knowledge
@app.route('/reset', methods=['POST'])
def reset():
    global MAP_INFO
    global PACKAGE_INFO
    global ROBOT_INFO
    global PLANNED_PATH
    MAP_INFO = None
    PACKAGE_INFO = []
    ROBOT_INFO = None
    PLANNED_PATH = None
    print("Knowledge reset")
    return "success"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
