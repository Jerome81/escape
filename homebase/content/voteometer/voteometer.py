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

last_used = "TIME" #TODO

@voteometer.get("/vote/<number>")
def vote(number):
    last_used = "TIME"
    n = int(number)
    if (n < 1 or n > 4):
        return "Illegal vote: %s" % number
    else:
        db[len(db)] = n
        db.commit()
        counter.vote(n)
        return "Voted %s" % number

@voteometer.get("/count")
def count():
    return str(counter.total_votes)

@voteometer.get("/average")
def average():
    return str(counter.average())

@voteometer.get("/stats")
def stats():
    return ("Last Used: %s / Status: %s" % (last_used, status))


