from flask import Flask, request, jsonify, send_file
from sqlitedict import SqliteDict
from datetime import date
import shutil
import os


central = Flask(__name__)
content_dir = "D:/code/content/"


@central.get("/outposts")
def get_outposts():
    return jsonify(outposts)

@central.post("/outpost")
def add_outpost():
    if request.is_json:
        outpost = request.get_json()
        print(outpost)
        outpost["last_seen"] = date.today().strftime("%d.%m.%Y")
        save(outpost["name"], outpost)
        return outpost, 201
    return {"error": "Request must be JSON"}, 415

def save(key, value, cache_file="outposts.sqlite3"):
    print("Signal received from outpost. Saving connection data.")
    print(value)
    try:
        with SqliteDict(cache_file) as outposts:
            outposts[key] = value 
            outposts.commit() 
    except Exception as ex:
        print("Error during storing data (Possibly unsupported):", ex)

@central.get("/outpost")
def get_outpost():
    return jsonify(find_outpost(request.args["id"]))
 
def find_outpost(key, cache_file="outposts.sqlite3"):
    try:
        with SqliteDict(cache_file) as outposts:
            value = outposts[key] # No need to use commit(), since we are only loading data!
        return value
    except Exception as ex:
        print("Error during loading data:", ex)


@central.get("/content")
def get_content():
    id = request.args["id"]
    folder = content_dir + id
    print("Requested content from: " + folder)
    
#    os.remove(temp_file)
    shutil.make_archive(folder, 'zip', folder)
    return send_file(folder + ".zip")
