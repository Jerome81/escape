import sys
sys.path.append('../')

import time
import json

from flask import Flask, send_from_directory
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit, disconnect

import paho.mqtt.client as mqtt

game = Flask(__name__)
cors = CORS(game)
game.config['CORS_HEADERS'] = 'Content-Type'

cache = {}

# The callback for when the client receives a CONNACK response from the server.
def on_connect_game(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("spacehunter/game")


# The callback for when a PUBLISH message is received from the server.
def on_message_game(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    event = json.loads(msg.payload)
    if event["event"] == "spaceship_ready":
        print("Spaceship Ready")
        pass

    if event["event"] == "select_start_position":
        print("Selected start position")       
        pass

def on_message_spaceship(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


# The callback for when the client receives a CONNACK response from the server.
def on_connect_spaceship(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("spacehunter/game")

gamemq = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
gamemq.on_connect = on_connect_game
gamemq.on_message = on_message_game

gamemq.connect("192.168.178.55", 1884, 60)

print("starting message queue for game started.")
gamemq.loop_start()

spaceship1mq = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
spaceship1mq.on_connect = on_connect_spaceship
spaceship1mq.on_message = on_message_spaceship

spaceship1mq.connect("192.168.178.55", 1883, 60)

print("starting message queue for spaceship 1.")
spaceship1mq.loop_start()
