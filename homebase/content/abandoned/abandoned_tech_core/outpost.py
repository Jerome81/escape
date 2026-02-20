from time import sleep
from time import time

from random import randint
import json
import paho.mqtt.client as mqtt
import gpiozero
import neopixel
import board
import os
import RPi.GPIO as GPIO

mq_ip = "192.168.5.11"
deviceId = "abandoned_tech_core"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"
_core_removed = False


light = neopixel.NeoPixel(board.D18, 12, brightness = 1, auto_write = True)
light.fill((255, 255, 255))

core = gpiozero.Button(23, hold_time = 0.2, bounce_time = 0.2)

# initialize door
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: Core herausnehmen"),
}

core.when_pressed = lambda: on_reset()
core.when_released = lambda: on_solved()

def lock_door():
    GPIO.setup(12, GPIO.LOW)
    print("Door locked")

def unlock_door():
    GPIO.setup(12, GPIO.HIGH)
    print("Door unlocked")

### Game events ###
def on_event(event):
    if event == "Core access granted":
        on_activate()

### Global commands ###
def on_started():
    global _gameState
    _gameState = "STARTED"
    sendUpdate()    

def on_stopped():
    global _gameState
    _gameState = "STOPPED"
    sendUpdate()

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    
def sendUpdate():
    jsonData = _jsonData
    
    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except Exception as e:
        print(e)

    jsonData["state"] = _puzzleState
    if _core_removed and _puzzleState == "INACTIVE":
        jsonData["input"] = "!!! INACTIVE - CORE REMOVED !!!"
    else:
        if _core_removed:
            jsonData["input"] = "CORE ENTFERNT"
        else:
            jsonData["input"] = "CORE DRIN"
    
    jsonData["game_state"] = ("%s - %s" % (_gameState, cpu_temp))
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))

def play_sound(file):
    os.system("mpg321 %s" % file)
    

### Puzzle commands ###
def on_solved():
    global _puzzleState
    global _core_removed
    
    _core_removed = True
    print("Core removed")
    sendUpdate()
    if _puzzleState == "INACTIVE":
        print("Core removed while inactive, ignoring.")
        return
    
    _puzzleState = "SOLVED"
    
    light.fill((255, 0, 0))
    jsonData = {
        "event": "Power down",
        "timestamp": time() * 1000
    }
    mqttc.publish("ToDevice/All", json.dumps(jsonData)) 

    sleep(3)

    jsonData = {
        "event": "Core removed",
        "timestamp": time() * 1000
    }
    mqttc.publish("ToDevice/All", json.dumps(jsonData)) 



def on_reset():
    global _puzzleState
    global _core_removed
    print("inserted")
    _puzzleState = "INACTIVE"
    _core_removed = False
    sendUpdate()
    lock_door()
    light.fill((0, 255, 0))    

def on_activate():
    global _puzzleState
    _puzzleState = "ACTIVE"
    unlock_door()
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
                on_reset()
        if 'event' in payload:
            on_event(payload["event"])
        if 'language' in payload:
            on_language_change(payload["language"])
            

    if msg.topic == "ToDevice/%s" % deviceId:
        if 'command' in payload:
            command = payload["command"]
            if command == "SOLVED":
                on_solved()
            if command == "RESET":
                on_reset()
            if command == "ACTIVATE":
                on_activate()


def connect(client):
    disconnected = True
    while disconnected:
        try:   
            client.connect(mq_ip, 1883, 60)
            light.fill((0, 255, 0))
            disconnected = False
            sendUpdate()
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

lock_door()

leds = []
color = (0, 255, 0)
try:
    while(True):
        if len(leds) == 0:
            leds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            if color == (0, 255, 0):
                color = (0, 255, 255)
            else:
                color = (0, 255, 0)
        
        if _gameState == "STARTED" and not _core_removed:
            l = leds.pop(randint(0, len(leds) - 1))
            light[l] = color
        sleep(0.05)

except Exception as e:
    print('An exception occurred: {}'.format(e))

