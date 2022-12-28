from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:admin@cluster0.nwcrbvw.mongodb.net/?retryWrites=true&w=majority")
db = cluster["autodb"]
collection_map = db["map_info"]
collection_package = db["package_info"]
collection_robot = db["robot_info"]

#insert on loop json from client.on_message for different collection
#ON PROGRESS - NEED DUMMY DATA TO INSERT ON LOOP
collection_map.insert_one({"map" : [[1,0,0], [0,0,1], [1,0,0]]})
collection_package.insert_one({"id_package": 1, "source":  [0,0], "destination": [1,1], "priority": "3"})
collection_robot.insert_one({"state" : "fetching package", "position" :  [1,0]})



