import os
import json
from pathlib import Path

def get_config():
    home = Path.home().as_posix()

    if not os.path.exists(home + '/quizzer.json'):
        print(home + "/quizzer.json doesn't exist. Please create.")
        data = {
            "room_id": "QUIZZERJSONMISSING",
            "station_id": "1",
            "mq_ip": "127.0.0.1",
        }
        return data

    with open(home + '/quizzer.json') as json_file:
        data = json.load(json_file)
        data["home"] = home
        return data

    return "" #TODO: Do something better