import os
import paho.mqtt.client as mqtt
import json
import gpiozero
import board
import neopixel
import RPi.GPIO as GPIO

from time import sleep

deviceId = "rippli"

mq_ip = "192.168.5.11"

_gameState = "STARTED"
_puzzleState = "ACTIVE"

_solution = "Button needs to be pressed while ACTIVE"

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}

VIDEOS = 3
next_button = gpiozero.Button(14, hold_time = 0.05, bounce_time = 0.1)
prev_button = gpiozero.Button(15, hold_time = 0.05, bounce_time = 0.1)
current_video = -1

def on_next():
    global current_video
    current_video = current_video + 1
    if current_video >= VIDEOS:
        current_video = VIDEOS
        publish("Show end")
    else:
        publish("video_%s" % current_video)
    sendUpdate()


def on_prev():  
    global current_video
    current_video = current_video - 1
    if current_video < 0:
        current_video = -1
        publish("Show start")
    else:
        publish("video_%s" % current_video)
    sendUpdate()

def publish(what):
    jsonData = {
        "display": what
    }
    mqttc.publish("ToDevice/%s_screen" % deviceId, json.dumps(jsonData))


def sendUpdate():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except Exception as e:
        print(e)

    jsonData = _jsonData
    jsonData["input"] = ("video_%s playing" % current_video)
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = ("%s - %s" % (_gameState, cpu_temp))
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))
    
    
### Game events ###
def on_event(event):
    pass

### Global commands ###
def on_started():
    publish("Show start")

def on_stopped():
    pass

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    
### Puzzle commands ###
def on_solved(client):
    pass

def on_reset(client):
    global current_video
    current_video = -1

def on_activate():
    global _puzzleState
    _puzzleState = "ACTIVE"
    sendUpdate()


### Message Queue Events ###

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    jsonData = _jsonData
    jsonData["status"] = "Connected"

    client.subscribe("ToDevice/%s" % deviceId)
    client.subscribe("ToDevice/All")
    client.publish("ToHost", json.dumps(jsonData))
    client.publish("FromDevice/%s" % deviceId, json.dumps(_jsonData))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global _gameState
    print(msg.topic)
    print(msg.payload)
    payload = json.loads(msg.payload.decode('utf-8'))

    if msg.topic == "ToDevice/All":
        if 'gameState' in payload:
            _gameState = payload["gameState"]
            if _gameState == "STARTED":
                on_started()
            if _gameState == "STOPPED":
                on_stopped()
            if _gameState == "RESET":
                on_reset(client)
        if 'event' in payload:
            on_event(payload["event"])
        if 'language' in payload:
            on_language_change(payload["language"])
            

    if msg.topic == "ToDevice/%s" % deviceId:
        if 'command' in payload:
            command = payload["command"]
            if command == "SOLVED":
                on_solved(client)
            if command == "RESET":
                on_reset()
            if command == "ACTIVATE":
                on_activate()

def connect(client):
    disconnected = True
    while disconnected:
        try:   
            client.connect(mq_ip, 1883, 60)
            disconnected = False
        except Exception as e:
            print('An exception occured: {}'.format(e))
            sleep(5)

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

connect(mqttc)

print("starting message queue.")
mqttc.loop_start()

next_button.when_pressed = lambda: on_next()
prev_button.when_pressed = lambda: on_prev()

try:
    while True:       
        sleep(0.1)
        
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
