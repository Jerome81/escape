import threading

from datetime import datetime
from sqlitedict import SqliteDict
from flask import Flask
from counter import Counter

voteometer = Flask(__name__)
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

last_used = datetime.now("%d.%m.%Y - %H:%M:%S")

@voteometer.get("/vote/<number>")
def vote(number):
    last_used = datetime.now("%d.%m.%Y - %H:%M:%S")
    n = int(number)
    if (n < 1 or n > 4):
        return "Illegal vote: %s" % number
    else:
        x = threading.Thread(target = send_vote, args=(n,))
        x.start()
        return "Voted %s" % number

def send_vote(n):
    db[len(db)] = n
    db.commit()
    counter.vote(n)
    counter.display_last_vote()
    counter.show_average()
        

@voteometer.get("/count")
def count():
    return str(counter.total_votes)

@voteometer.get("/average")
def average():
    return str(counter.average())

@voteometer.get("/status")
def status():
    return ("Last Used: %s / Status: %s" % (last_used, status))

@voteometer.get("/attentionmode")
def attentionmode():
    counter.play_loaded_animation()
