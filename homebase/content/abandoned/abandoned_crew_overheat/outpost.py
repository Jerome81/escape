import paho.mqtt.client as mqtt
import serial
import os
import time
from time import sleep
import json

import gpiozero
import RPi.GPIO as GPIO

deviceId = "abandoned_crew_overheat"

mq_ip = "192.168.5.11"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"
_solution = "LEFT-MIDDLE-RIGHT"
_currentData = ""
_left = ""
_right = ""
_middle = ""

_jsonData = {
    "id": deviceId,
    "description": ( _solution ),
}

button1 = gpiozero.Button(18, hold_time = 0.1, bounce_time = 0.2)
button2 = gpiozero.Button(23, hold_time = 0.1, bounce_time = 0.2)
button3 = gpiozero.Button(24, hold_time = 0.1, bounce_time = 0.2)

# initialize heaters
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

def start_heaters():
    GPIO.setup(12, GPIO.LOW)
    print("Heaters started")

def stop_heaters():
    GPIO.setup(12, GPIO.HIGH)
    print("Heaters stopped")

def sendUpdate():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except e:
        print(e)

    jsonData = _jsonData
    jsonData["input"] = (_currentData))
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = ("%s - %s" % (_gameState, cpu_temp))
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))

### Game events ###
def on_event(event):
    if event == "Heatgun produced":
        on_activate()



### Global commands ###
def on_started():
    pass

def on_stopped():
    pass

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    

### Puzzle commands ###
def on_solved(client):
    global _puzzleState
    _puzzleState = "SOLVED"
    sendUpdate()
    stop_heaters()
    jsonData = {
        "event": ("Overheat solved")
    }
    client.publish("ToDevice/All", json.dumps(jsonData))

def on_unsolved(client):
    on_activate()
    
def on_reset(client):
    global _puzzleState
    _puzzleState = "RESET"
    stop_heaters()
    sendUpdate()

def on_activate():
    global _puzzleState
    _puzzleState = "ACTIVE"
    start_heaters()
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
                on_reset(client)
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

def left(inOut):
    global _left
    global _currentData
    print("Left: %s" % inOut)
    _left = inOut
    _currentData = _left + _middle + _right
    sendUpdate()

def middle(inOut):
    global _middle
    global _currentData
    print("Middle: %s" % inOut)
    _middle = inOut
    _currentData = _left + _middle + _right
    sendUpdate()

def right(inOut):
    global _right
    global _currentData
    print("Right: %s" % inOut)
    _right = inOut
    _currentData = _left + _middle + _right
    sendUpdate()

button1.when_pressed = lambda: left("LEFT-")
button1.when_released = lambda: left("")

button2.when_pressed = lambda: middle("MIDDLE-")
button2.when_released = lambda: middle("")

button3.when_pressed = lambda: right("RIGHT")
button3.when_released = lambda: right("")

stop_heaters()

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

connect(mqttc)

print("starting message queue.")
mqttc.loop_start()

try:    
    while True:
        if _currentData == _solution:
            on_solved()
        sleep(0.1)
       

except Exception as e:
    s = ('An exception occurred: {}'.format(e))
    _currentData = s
    sendUpdate()
    print(s)
    print("Cleaning up")