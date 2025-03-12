import RPi.GPIO as GPIO
import time
from effects import Effects

import paho.mqtt.client as mqtt
import json
import board
import traceback
from random import randint

from time import sleep
from datetime import datetime, timedelta

deviceId = "communicator"

mq_ip = "192.168.178.11"

_gameState = "STOPPED"
LEDS = 100

_jsonData = {
    "id": deviceId,
    "description": "Lights and screen",
}

effects = Effects(led_count=LEDS, pin=board.D18)
powered_up = False

PAUSE_COLOR = ((0, 0, 130))
GAME_COLOR = ((50, 255, 50))
NOT_STARTED_COLOR = ((0, 255, 0))

### Game events ###
def on_event(event):
    global powered_up
    if event == "Power up":
        powered_up = True
        effects.just_light(GAME_COLOR)
    if event == "Power down":
        powered_up = False
        effects.start_red_alert()
    if event == "Self destruct":
        effects.fill((0, 0, 0))  # replace with something cooler
    if event == "Upload successful":
        effects.fill((0, 0, 0))  # replace with something cooler
    if event == "Core removed":
        pass

### Global commands ###
def on_started():
    if powered_up:
        effects.just_light(GAME_COLOR)
    else:
        effects.start_red_alert()

def on_stopped():
    effects.just_light(PAUSE_COLOR)

def on_reset():
    pass

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    

### Puzzle commands ###
def on_display(client):
    pass

 
### Message Queue Events ###

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    jsonData = _jsonData
    jsonData["status"] = "Connected"

    client.subscribe("ToDevice/%s" % deviceId)
    client.subscribe("ToDevice/All")
    effects.morph((255, 255, 0), NOT_STARTED_COLOR, target_brightness = 0.7)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global _last_animation
    global _current_animation
    print(msg.topic)
    print(msg.payload)
    payload = json.loads(msg.payload.decode('utf-8'))

    print(payload)
    if msg.topic == "ToDevice/All":
        if 'gameState' in payload:
            _gameState = payload["gameState"]
            if _gameState == "STARTED":
                on_started()
            if _gameState == "STOPPED":
                on_stopped()
            if _gameState == "RESET":
                on_reset()
        if 'event' in payload:
            on_event(payload["event"])
        if 'language' in payload:
            on_language_change(payload["language"])
            

    if msg.topic == "ToDevice/%s" % deviceId:
        if 'command' in payload:
            command = payload["command"]
            if command == "DISPLAY":
                on_display(client)
            

   


_connected = False
_next_connection_try = None
_next_connection_delay = timedelta(seconds=10)

def connect(client):
    global _next_connection_try
    global _connected
    if _next_connection_try is None or _next_connection_try < datetime.now():
        _next_connection_try = datetime.now() + _next_connection_delay
        try:   
            client.connect(mq_ip, 1883, 60)
            client.loop_start()
            _connected = True
        except Exception as e:
            print('An exception occured: {}'.format(e))

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

counter = 0
try:
    while True:
        if not _connected:
            connect(mqttc)
        effects.next_iteration()
        sleep(0.05)

except Exception as e:
    print('An exception occurred: {}'.format(e))
    print(traceback.format_exc())
    print("Cleaning up")
    GPIO.cleanup()
