import sys
sys.path.append('../')

import time
import threading
import json

from flask import Flask, send_from_directory
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit, disconnect

import paho.mqtt.client as mqtt

captain = Flask(__name__)
cors = CORS(captain)
captain.config['CORS_HEADERS'] = 'Content-Type'

socket_ = SocketIO(captain, async_mode=None)
cache = {}

torpedo_enabled = False

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("spacehunter/spaceship")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    event = json.loads(msg.payload) # ["jump_complete", ["1", "5", "4", "1234"]]
    print(event)
    cache["event"] = [event["event"], event["data"]]
    
    #cache["event"] = ["jump_complete", "123"]

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("192.168.178.55", 1883, 60)

print("starting message queue.")
mqttc.loop_start()
mqttc.publish("spacehunter/spaceship/register", "captain")

@captain.route('/<path:path>')
def send_report(path):
    return send_from_directory('', path)


@captain.get("/initiate_jump/<direction>")
@cross_origin
def initiate_jump(direction):
    pass

@captain.get("/jump_executed/<direction>")
@cross_origin()
def jump_executed(direction):
    pass

@captain.post("/enable_torpedo")
@cross_origin()
def enable_torpedo():
    torpedo_enabled = True

    # light up Torpedo Button.


@captain.get("/fire_torpedo/<location>")
@cross_origin()
def fire_torpedo(location):
    torpedo_enabled = False

    # unlight Torpedo Button.


@socket_.on('needs_refresh', namespace='/refresh')
def refresh(data):
    while True:
        try:
            # print(".", end = " ")

            if "event" in cache:
                # print("Checking refresh on ", threading.currentThread(), " - ", cache["event"])
                print("Refreshing")
                emit('refresh', {'event': cache["event"][0], 'data': cache["event"][1]})
                del cache["event"]
            
            
               
        except Exception as ex:
            print(ex)

        time.sleep(0.1) 


################################################
## Callbacks

@captain.get("/jump_complete/<direction>/<newX>/<newY>/<possibleDirs>")
def jump_complete(direction, newX, newY, possibleDirs):
    print("Triggering refresh on ", threading.currentThread())
    cache["event"] = ["jump_complete", possibleDirs]
    return "OK"

