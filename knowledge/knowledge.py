from flask import Flask, request
from pymongo import MongoClient
import json
import logging

# connecting to MongoDB
# client = MongoClient(
#     "mongodb+srv://admin:admin@cluster0.nwcrbvw.mongodb.net/?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)

client = MongoClient("mongodb://localhost:27017/")

db = client["autodb"]
# 4 collections: map_info, package_info, robot_info, planned_path
collection_map_info = db["map_info"]
collection_package_info = db["package_info"]
collection_robot_info = db["robot_info"]
collection_planned_path = db["planned_path"]

app = Flask(__name__)

print("Knowledge is running...")


@app.route('/map_info', methods=['GET', 'POST'])
def map_info():
    if request.method == 'POST':  # insert map_info document
        map_info = json.loads(request.data)
        collection_map_info.insert_one({"map_info": map_info}).inserted_id
        print("Map info inserted:", map_info)
        # return status 200
        return "success"
    else:
        # fetch last map_info document
        try:
            last_map_document = list(
                collection_map_info.find().sort("_id", -1).limit(1))[0]['map_info']
        except IndexError:
            print("No map found")
            return json.dumps(None)
        print("Get map info:", last_map_document)
        return json.dumps(last_map_document)


@app.route('/package_info', methods=['GET', 'POST', 'DELETE'])
def package_info():
    if request.method == 'POST':  # insert package_info document
        package_info = json.loads(request.data)
        collection_package_info.insert_one({"id": package_info['id'], "source":  package_info['source'],
                                            "destination": package_info['destination']}).inserted_id
        print("Package info inserted:", package_info)
        return "success"
    elif request.method == 'GET':
        # fetch first package_info document (FIFO)
        try:
            first_package_document = list(
                collection_package_info.find().sort({"_id": 1}).limit(1))
            if len(first_package_document) == 0:
                print("No package info found")
                first_package_document = None
            else:
                first_package_document = first_package_document[0]
        except IndexError:
            print("No package info found")
            first_package_document = None
        # collection_package_info.remove(first_package_document)
        print("Get package info:", first_package_document)
        return json.dumps(first_package_document)
    elif request.method == 'DELETE':
        # delete package with given id
        package_id = request.args.get('package_id')
        collection_package_info.delete_one({"id": package_id})
        print("Package info deleted:", package_id)
        return "success"


@app.route('/robot_info', methods=['GET', 'POST'])
def robot_info():
    if request.method == 'POST':  # insert robot_info document
        robot_info = json.loads(request.data)
        collection_robot_info.insert_one(
            {"state": robot_info['state'], "position":  robot_info['position']})
        print("Robot info inserted:", robot_info)
        return "success"
    elif request.method == 'GET':
        # fetch last robot_info document
        try:
            last_robot_document = list(
                collection_robot_info.find().sort("_id", -1).limit(1))
            if len(last_robot_document) == 0:
                last_robot_document = None
            else:
                last_robot_document = last_robot_document[0]
        except IndexError:
            last_robot_document = None
        print("Get robot info:", last_robot_document)
        return json.dumps(last_robot_document)


@app.route('/planned_path', methods=['GET', 'POST'])
def planned_path():
    if request.method == 'POST':  # insert planned_path document
        planned_path = json.loads(request.data)
        collection_planned_path.insert_one(
            {"package_id": planned_path['package_id'], "planned_path": planned_path['planned_path']})
        print("Planned path inserted:", planned_path)
        return "success"
    else:  # fetch last planned_path document
        last_path_document = json.loads(
            collection_planned_path.find().sort("_id", -1).limit(1))
        print("Get planned path:", last_path_document)
        return json.dumps(last_path_document)


# reset knowledge
@app.route('/reset', methods=['POST'])
def reset():
    collection_map_info.delete_many({})
    collection_package_info.delete_many({})
    collection_robot_info.delete_many({})
    collection_planned_path.delete_many({})
    print("Knowledge reset")
    return "success"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
