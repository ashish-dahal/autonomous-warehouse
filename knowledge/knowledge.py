from flask import Flask, request
from pymongo import MongoClient
import json

# connecting to MongoDB
client = MongoClient(
    "mongodb+srv://admin:admin@cluster0.nwcrbvw.mongodb.net/?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)

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
        map_info = request.get_json()
        collection_map_info.insert_one({"map_info": map_info}).inserted_id
        # return status 200
        return "success"
    else:
        # fetch last map_info document
        last_map_document = list(
            collection_map_info.find().sort("_id", -1).limit(1))[0]['map_info']
        print(last_map_document)
        return json.dumps(last_map_document)


@app.route('/package_info', methods=['GET', 'POST'])
def package_info():
    if request.method == 'POST':  # insert package_info document
        package_info = request.get_json()
        collection_package_info.insert_one({"id": package_info['id'], "source":  package_info['source'],
                                            "destination": package_info['destination']}).inserted_id
    else:  # fetch first package_info document (FIFO)
        first_package_document = list(
            collection_package_info.find().sort({"_id": 1}).limit(1))
        # collection_package_info.remove(first_package_document)
        return json.dumps(first_package_document)


@app.route('/robot_info', methods=['GET', 'POST'])
def robot_info():
    if request.method == 'POST':  # insert robot_info document
        robot_info = request.get_json()
        collection_robot_info.insert_one(
            {"state": robot_info['state'], "position":  robot_info['position']})
    else:  # fetch last robot_info document
        last_robot_document = json.loads(
            collection_robot_info.find().sort("_id", -1).limit(1))
        return json.dumps(last_robot_document)


@app.route('/planned_path', methods=['GET', 'POST'])
def planned_path():
    if request.method == 'POST':  # insert planned_path document
        planned_path = request.get_json()
        collection_planned_path.insert_one(
            {"package_id": planned_path['package_id'], "planned_path": planned_path['planned_path']})
    else:  # fetch last planned_path document
        last_path_document = json.loads(
            collection_planned_path.find().sort("_id", -1).limit(1))
        return json.dumps(last_path_document)


# reset knowledge
@app.route('/reset', methods=['POST'])
def reset():
    collection_map_info.delete_many({})
    collection_package_info.delete_many({})
    collection_robot_info.delete_many({})
    collection_planned_path.delete_many({})
    print("Knowledge reset")


if __name__ == '__main__':
    app.run()
