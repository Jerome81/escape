
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
import gpiozero

from random import randint
from time import sleep


mq_ip = "192.168.5.11"
deviceId = "abandoned_crew_exit"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"

# initialize door
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

_jsonData = {
    "id": deviceId,
    "description": ("Ausgangstüre"),
}

def lock_door():
    GPIO.setup(12, GPIO.LOW)
    print("Door locked")

def unlock_door():
    GPIO.setup(12, GPIO.HIGH)
    print("Door unlocked")

def sendUpdate():
    jsonData = _jsonData
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = _gameState
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))

### Game events ###
def on_event(event):
    if _gameState == "STARTED":
        if  event == "Core removed":
            on_solved()

        if  event == "Self destruct":
            on_solved()

        if  event == "Mystery solved":
            on_solved()       
        
        if  event == "Out of oxygen":
            on_solved()

        if  event == "AI won":
            on_solved()


### Global commands ###
def on_started():
    on_activate()

def on_stopped():
    global _puzzleState
    _puzzleState == "INACTIVE"

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    

### Puzzle commands ###
def on_solved():
    global _puzzleState
    _puzzleState = "SOLVED"
    sendUpdate()
    jsonData = {
        "event": "Exit door unlocked"
    }
    mqttc.publish("ToDevice/All", json.dumps(jsonData))
    unlock_door()
    mqttc.publish("cmnd/sleeping_pods/Power", "off")

def on_reset():
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
                on_reset()
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

lock_door()

try:
    while True:
        #print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))
        sleep(0.2)
except Exception as e:
    print('An exception occurred: {}'.format(e))
finally:
    GPIO.cleanup
