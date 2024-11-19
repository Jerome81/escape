from flask import Flask
from flask_cors import CORS, cross_origin

captain = Flask(__name__)
cors = CORS(captain)
captain.config['CORS_HEADERS'] = 'Content-Type'

torpedo_enabled = False

direction_cards = "1234"

@captain.get("/get_possible_directions")
def get_possible_directions():
    return direction_cards

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