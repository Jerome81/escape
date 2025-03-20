import sys
sys.path.append('../')

import time
import threading
import json
import wave
import sys
import pyaudio

from flask import Flask, send_from_directory
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit, disconnect

import paho.mqtt.client as mqtt

communicator = Flask(__name__)
cors = CORS(communicator)
communicator.config['CORS_HEADERS'] = 'Content-Type'

socket_ = SocketIO(communicator, async_mode=None)
cache = {}

torpedo_enabled = False

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("abandoned", 0)
    client.subscribe("abandoned/comms", 0)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "abandoned/comms":
        play(msg.payload.decode("utf-8"))
    #event = json.loads(msg.payload) # ["jump_complete", ["1", "5", "4", "1234"]]
   # print(event)
   # cache["event"] = [event["event"], event["data"]]
    
    #cache["event"] = ["jump_complete", "123"]

CHUNK = 1024

def play(name):
    with wave.open("/var/lib/outposts/%s" % name, 'rb') as wf:
        # Instantiate PyAudio and initialize PortAudio system resources (1)
        p = pyaudio.PyAudio()

        # Open stream (2)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Play samples from the wave file (3)
        while len(data := wf.readframes(CHUNK)):  # Requires Python 3.8+ for :=
            stream.write(data)

        # Close stream (4)
        stream.close()

        # Release PortAudio system resources (5)
        p.terminate()


mqttc = mqtt.Client("valves_1")
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("192.168.178.11", 1883, 60)

print("starting message queue.")
mqttc.loop_start()
mqttc.publish("abandoned/register", "valves")


while(True):
    time.sleep(1)


@mqtest.get("/attraction_mode")
@cross_origin
def attraction_mode(direction):
    mqttc.publish("spacehunter/game", "attraction mode Valves")
