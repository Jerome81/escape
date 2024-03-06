import threading

from datetime import datetime
from sqlitedict import SqliteDict
from flask import Flask
from counter import Counter
from flask_cors import CORS, cross_origin

voteometer = Flask(__name__)
cors = CORS(voteometer)
voteometer.config['CORS_HEADERS'] = 'Content-Type'

db = SqliteDict("votes.sqlite")

status = "Loading."

counter = Counter()
for key, item in db.items():
    print(item)
    counter.vote(item)

status = "Loaded."
counter.play_loaded_animation()

counter.show_average()
status = "Ready."

last_used = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
counter.turn_button_lights_on()

@voteometer.get("/vote/<number>")
@cross_origin()
def vote(number):
    last_used = datetime.now().strftime("%d.%m.%Y - %H:%M:%S")
    n = int(number)
    if (n < 1 or n > 4):
        return "Illegal vote: %s" % number
    else:
        x = threading.Thread(target = send_vote, args=(n,))
        x.start()
        return "Voted %s" % number
    
def send_vote(n):
    db[len(db)] = n
    counter.turn_button_lights_off()
    counter.turn_button_light_on(n - 1)
    db.commit()
    counter.vote(n)
    counter.display_last_vote()
    counter.show_average()
    counter.turn_button_lights_on()
    
        
@voteometer.get("/stats")
@cross_origin()
def stats():
    return "Total votes: %s<br/>Average: %s" % (str(counter.total_votes), str(counter.average())), 200

@voteometer.get("/status")
@cross_origin()
def status():
    return ("Last Used: %s / Status: %s" % (last_used, status)), 200

@voteometer.get("/attraction_mode")
@cross_origin()
def attraction_mode():
    counter.play_loaded_animation()
    return "Caught the attention of people", 200
