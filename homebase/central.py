from flask import Flask, request, jsonify, send_file
from sqlitedict import SqliteDict
from datetime import datetime
from config import get_config
import shutil
import os

DATE_FORMAT = "%d.%m.%Y - %H:%M:%S"
central = Flask(__name__)
content_dir = get_config()["content_dir"]
print(content_dir)

# Removing old entries
with SqliteDict("outposts.sqlite3") as outposts:
    for key in outposts:
        o = outposts[key]
        try:
            print(o["last_seen"])
            last_seen = datetime.strptime(o["last_seen"], DATE_FORMAT)
            print(datetime.now() - last_seen)
            if ((datetime.now() - last_seen).days > 7):
                print("Removing outpost, because we didn't have contact for more than 7 days.")
                del outposts[key]
                outposts.commit()

        except Exception as ex:
            print(ex)
            print("Removing the following outpost, because I can't determine when we last had contact: %s" % o)
            del outposts[key]
            outposts.commit()


@central.get("/outpostsjson")
def get_outposts_json(cache_file="outposts.sqlite3"):
    try:
        all = {}
        with SqliteDict(cache_file) as outposts:
            for key in outposts:
                all[key] = outposts[key]
               
        
        return jsonify(all)
    except Exception as ex:
        print("Error while loading outposts data:", ex)
        return "Error"

@central.get("/outposts")
def get_outposts(cache_file="outposts.sqlite3"):
    try:
        all = {}
        page = """<html><head>
        <link rel='stylesheet' href='/static/styles.css'/>
        <script src="/static/jquery-3.6.0.min.js"></script>
        <script>
        function send_request(type, ip, method, resultDiv)
        {
            $.ajax({

                type: type,
                url: 'http://' + ip + '/' + method,
                success: function(data) {
                    $('#' + resultDiv).html(data);
                },
                error: function(data) {
                    $('#' + resultDiv).html(data);
                }
            });

        }
        </script>
        </head>
        <body>%s</body>
        </html>"""
        cards = ""
        i = 0
        with SqliteDict(cache_file) as outposts:
            for key in outposts:
                i = i + 1
                o = outposts[key]
                all[key] = outposts[key]
                c = """<div class='card'>
                <div class='title'>%s</div>
                <div class='status'><b>Status:</b><br/>%s</div>
                <div class='actions'>%s</div>
                <div class='result' id='result""" + str(i) + """'></div>
                </div>"""
                try:
                    cards = cards + (c % (o["name"] + " - " + o["last_seen"], o["status"] + " - " + o["IP"], get_actions(o, i, o["IP"])))
                except:
                    cards = cards + (" - couldn't load data for: %s" % o["name"])

        
        return (page % cards)
    except Exception as ex:
        print("Error while loading outposts data:", ex)
        print(o)
        return "Error"
    
def get_actions(outpost, number, ip):
    
    resultDiv = "result" + str(number)
    action_template = "<a onclick=\"send_request('%s', '%s', '%s', '" + resultDiv + "')\" class='button' >%s</a>"
    actions = ""
    actions = actions + action_template % ("GET", ip + ":5001", "status", "Boot Status")
    actions = actions + action_template % ("GET", ip + ":5001", "download", "Download")
    actions = actions + action_template % ("GET", ip + ":5001", "reboot?pwd=why_not", "Reboot")
    actions = actions + action_template % ("GET", ip + ":5002", "attraction_mode", "Attraction mode")
    actions = actions + action_template % ("GET", ip + ":5002", "stats", "Statistics")
    actions = actions + action_template % ("GET", ip + ":5002", "status", "Status")
    return actions


@central.post("/outpost")
def add_outpost():
    if request.is_json:
        outpost = request.get_json()
        print(outpost)
        outpost["last_seen"] = datetime.now().strftime(DATE_FORMAT)
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
        print("Error while storing data (Possibly unsupported):", ex)

@central.get("/outpost")
def get_outpost():
    return jsonify(find_outpost(request.args["id"]))
 
def find_outpost(key, cache_file="outposts.sqlite3"):
    try:
        with SqliteDict(cache_file) as outposts:
            value = outposts[key] # No need to use commit(), since we are only loading data!
        return value
    except Exception as ex:
        print("Error while loading data:", ex)


@central.get("/content")
def get_content():
    id = request.args["id"]
    folder = content_dir + id
    print("Requested content from: " + folder)
    
#    os.remove(temp_file)
    if os.path.isdir(folder):
        shutil.make_archive(folder, 'zip', folder)
        return send_file(folder + ".zip")
    else:
        return "Directory not found", 404
