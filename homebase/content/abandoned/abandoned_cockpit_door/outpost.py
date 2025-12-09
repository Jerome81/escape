import os
import paho.mqtt.client as mqtt
import json
import gpiozero
import board
import neopixel
import RPi.GPIO as GPIO

from datetime import datetime, timedelta
from time import sleep

deviceId = "abandoned_cockpit_door"

mq_ip = "192.168.5.11"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"
PRESSED = 0
UNPRESSED = 1

_solution = "Button drücken wenn Overheat gelöst"

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}

BUTTON_PIN = 14  #GPIO14

button = gpiozero.Button(BUTTON_PIN, hold_time = 0.05, bounce_time = 0.2)


# initialize door
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

next_overheat_send = datetime.now()

def sendUpdate():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except Exception as e:
        print(e)

    jsonData = _jsonData
    jsonData["input"] = ""
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = ("%s - %s" % (_gameState, cpu_temp))
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))
    
def lock_door():
    GPIO.setup(12, GPIO.LOW)
    print("Door locked")

def unlock_door():
    GPIO.setup(12, GPIO.HIGH)
    print("Door unlocked")


### Game events ###
def on_event(event):
    if  event == "Overheat solved":
        on_activate()

### Global commands ###
def on_started():
    sendUpdate()

def on_stopped():
    pass

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    

### Puzzle commands ###
def on_solved(client):
    global _puzzleState
    global next_overheat_send

    if _gameState == "STARTED" and _puzzleState != "SOLVED":
        if _puzzleState == "ACTIVE":
            _puzzleState = "SOLVED"
            unlock_door()
            sendUpdate()
            jsonData = {
                "event": "Cockpit door open"
            }
            client.publish("ToDevice/All", json.dumps(jsonData))
        else:
            if datetime.now() >= next_overheat_send:
                jsonData = {
                    "display": "Cockpit overheated"
                }
                next_overheat_send = datetime.now() + timedelta(seconds=7)
                client.publish("ToDevice/Comms", json.dumps(jsonData))

def on_reset(client):
    global _puzzleState
    _puzzleState = "INACTIVE"
    lock_door()
    sendUpdate()

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

on_reset(mqttc)

button.when_pressed = lambda: on_solved(mqttc)

sendUpdate()

try:
    while True:       
        sleep(0.1)
        
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
