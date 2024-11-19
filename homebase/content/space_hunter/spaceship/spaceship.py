import json
import requests

from flask import Flask
from flask_cors import CORS, cross_origin

from direction_coordinator import DirectionCoordinator
from general.star_map import StarMap

import paho.mqtt.client as mqtt

spaceship = Flask(__name__)
cors = CORS(spaceship)
spaceship.config['CORS_HEADERS'] = 'Content-Type'

dc = DirectionCoordinator(direction_cards="1234", max_direction_cards = 4, curX = 5, curY = 5, map = StarMap.solarSystem())

required_modules = [
    "captain",
    "engineer",
    "comms",
    "officer",
    "map",
    "mainscreen"
]

registered_modules = {}
cache = {}

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("spacehunter/spaceship")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    cache["event"] = ["jump_complete", "123"]

spaceship_mq = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
spaceship_mq.on_connect = on_connect
spaceship_mq.on_message = on_message

spaceship_mq.connect("192.168.178.55", 1883, 60)

print("starting message queue.")
spaceship_mq.loop_start()
spaceship_mq.publish("spacehunter/spaceship/register", "spaceship")

@spaceship.get("/get_direction_sequence")
def get_direction_sequence():
    return json.dumps("1234");

@spaceship.get("/get_data")
def get_map():
    return dc.get_data()

@spaceship.get("/module/<type>/<url>/<status>")
def register(type, url, status):
    registered_modules[type] = [ url, status ]
    return "Done"

@spaceship.get("/move/<direction>")
def move(direction):
    if dc.move(direction):
        spaceship_mq.publish("spacehunter/spaceship", json.dumps({"event": "jump_complete", "data": [direction, dc.curX, dc.curY, dc.get_possible_directions() ]}))
        return "OK"
    else:
        return "Illegal"

@spaceship.get("/status")
def status():
    content = "<html><head>#HEAD</head><body>#BODY</body></html>"
    body = ""
    for module in required_modules:
        if module in registered_modules:
            body = body + "<div id='" + module + "' class='online'>" + module + " online at " + registered_modules[module][0] + "<div class='status'>" + registered_modules[module][1] + "</div><div class='actions'>" + get_actions(module) + "</div></div>"
        else:
            body = body + "<div id='" + module + "' class='missing'>" + module + " missing</div>"
    
    content = content.replace("#BODY", body)
    return content


def get_actions(module):
    if module == "captain":
        return "enable_torpedo / fire_torpedo / get_possible_directions / initiate_jump / jump_executed"
    
    if module == "map":
        return "redraw / reload"