import json

from flask import Flask
from flask_cors import CORS, cross_origin

from direction_coordinator import DirectionCoordinator
from general.star_map import StarMap

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

@spaceship.get("/get_direction_sequence")
def get_direction_sequence():
    return json.dumps("1234");

@spaceship.get("/get_data")
def get_map():
    return dc.get_data()

@spaceship.get("/register/<type>/<url>")
def register(type, url):
    registered_modules[type] = url
    return "Done"

@spaceship.get("/move/<direction>")
def move(direction):
    dc.move(direction)
    return "Done"

@spaceship.get("/status")
def status():
    content = "<html><head>#HEAD</head><body>#BODY</body></html>"
    body = ""
    for module in required_modules:
        if module in registered_modules:
            body = body + "<div id='" + module + "' class='online'>" + module + " online at " + registered_modules[module] + "<div class='actions'>" + get_actions(module) + "</div></div>"
        else:
            body = body + "<div id='" + module + "' class='missing'>" + module + " missing</div>"
    
    content = content.replace("#BODY", body)
    return content


def get_actions(module):
    if module == "captain":
        return "enable_torpedo / fire_torpedo / get_possible_directions / initiate_jump / jump_executed"
    
    if module == "map":
        return "redraw / reload"