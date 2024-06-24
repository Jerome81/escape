from flask import Flask
from flask_cors import CORS, cross_origin

captain = Flask(__name__)
cors = CORS(captain)
captain.config['CORS_HEADERS'] = 'Content-Type'

torpedo_enabled = False

last_direction = ""
allowed_direction_cards = 3
last_direction_card = 0

direction_cards = "1234"


def get_possible_directions():
    return direction_cards

@captain.get("/hyperspace_executed/<location>")
@cross_origin()
def hyperspace_executed(location):
    newlocation = location

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