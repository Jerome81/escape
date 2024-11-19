import sys
sys.path.append('../')

import threading
import json

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit, disconnect

import paho.mqtt.client as mqtt

import time
import subprocess

map_display = Flask(__name__)

cors = CORS(map_display)
map_display.config['CORS_HEADERS'] = 'Content-Type'

socket_ = SocketIO(map_display, async_mode=None)
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
    event = json.loads(msg.payload) # ["jump_complete", ["1", "5", "4", "1234"]]
    cache["event"] = [event["event"], event["data"]]
    print(cache)
    #print(cache["event"])

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("192.168.178.55", 1883, 60)

print("starting message queue.")
mqttc.loop_start()
mqttc.publish("spacehunter/spaceship/register", "map")

@map_display.route('/map')
def main():
    return render_template('map.html')

@map_display.route('/<path:path>')
def send_report(path):
    return send_from_directory('', path)

@map_display.get("/jump_complete/<direction>/<newX>/<newY>/<possibleDirs>")
def jump_complete(direction, newX, newY, possibleDirs):
    print("Triggering refresh on ", threading.currentThread())
    cache["event"] = ["jump_complete", [direction, newX, newY]]
    return "OK"

@socket_.on('needs_refresh', namespace='/refresh')
def refresh(data):
    while True:
        try:
            # print(".", end = " ")
            if "event" in cache:
                print("Refreshing ")
                print(cache["event"][0])
                print(cache["event"][1])
                emit('refresh', {'event': cache["event"][0], 'data': cache["event"][1]})
                del cache["event"]
                       
               
        except Exception as ex:
            print(ex)

        time.sleep(0.1) 


if __name__ == '__main__':
    socket_.run(map_display, host='0.0.0.0', port=80, debug=True)