from flask import Flask, request
from pymongo import MongoClient
import json

app = Flask(__name__)

client = MongoClient("mongodb+srv://admin:admin@cluster0.nwcrbvw.mongodb.net/?retryWrites=true&w=majority") #connecting to MongoDB

db = client["autodb"]
#4 collections: map_info, package_info, robot_info, planned_path
collection_map = db["map_info"]
collection_package = db["package_info"]
collection_robot = db["robot_info"]
collection_planned_path = db["planned_path"]

@app.route('/map_info', methods=['GET', 'POST'])
def map_info():
    if request.method == 'POST': #insert map_info document
        map_info = request.get_json()
        collection_map.insert_one({"map" : map_info['map']}).inserted_id
    else: #fetch last map_info document
        last_map_document = json.loads(collection_map.find().sort({_id:-1}).limit(1))
        return json.dumps(last_map_document)


@app.route('/package_info', methods=['GET', 'POST'])
def package_info():
    if request.method == 'POST': #insert package_info document
        package_info = request.get_json()
        collection_package.insert_one({"id_package" : package_info['id_package'], "source":  package_info['source'], "destination": package_info['destination'], "priority": package_info['priority']}).inserted_id
    else: #fetch first package_info document (FIFO)
        first_package_document = json.loads(collection_package.find().sort({_id:1}).limit(1))
        collection_package.remove(first_package_element)
        return json.dumps(last_package_document)

@app.route('/robot_info', methods=['GET', 'POST'])
def robot_info():
    if request.method == 'POST': #insert robot_info document
        robot_info = request.get_json()
        collection_robot.insert_one({"state" : robot_info['state'], "position" :  robot_info['position']})
    else: #fetch last robot_info document
        last_robot_document = json.loads(collection_robot.find().sort({_id:-1}).limit(1))
        return json.dumps(last_robot_document)

@app.route('/planned_path', methods=['GET', 'POST'])
def planned_path():
    if request.method == 'POST': #insert planned_path document
        planned_path = request.get_json()
        collection_planned_path.insert_one({"package_id" : planned_path['package_id'], "planned_path" : planned_path['planned_path']})
    else: #fetch last planned_path document
        last_path_document = json.loads(collection_planned_path.find().sort({_id:-1}).limit(1))
        return json.dumps(last_path_document)
