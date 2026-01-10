import sys
sys.path.append('../')

from common import configuration
from station import Station

config = configuration.get_config()
print(config)

def on_start_game():
    print("Starting")

station = Station()
station.on_start_game(on_start_game)

station.answer_selected(3) # sends selected answer and timestamp
