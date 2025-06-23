import paho.mqtt.client as mqtt
import json
import gpiozero
import board
import neopixel
import RPi.GPIO as GPIO
import os

from time import sleep

deviceId = "abandoned_crew_door"

mq_ip = "192.168.5.11"

_gameState = "STOPPED"
_puzzleState = "ACTIVE"
PRESSED = 0
UNPRESSED = 1

_solution = PRESSED
_currentData = UNPRESSED

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}

BUTTON_PIN = 14  #GPIO14

button = gpiozero.Button(BUTTON_PIN, hold_time = 1, bounce_time = 0.2)


# initialize door
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)


def sendUpdate():
    print("Game is: %s - Puzzle is: %s - Data: %s" % (_gameState, _puzzleState, _currentData))
    
    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except e:
        print(e)

    jsonData = _jsonData
    jsonData["input"] = _currentData
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
    pass

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
    unlock_door()
    sendUpdate()
    jsonData = {
        "event": "Crew door open"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))
    client.publish("cmnd/sleeping_pods/Power", "on")



def on_reset():
    global _puzzleState
    global _currentData
    _puzzleState = "ACTIVE"  # Always active
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

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

connect(mqttc)

print("starting message queue.")
mqttc.loop_start()

on_reset(mqttc)

button.when_pressed = lambda: on_solved(mqttc)

try:
    while True:
        
        if _gameState == "STOPPED":
            # Always be ready
            pass 
       
        sleep(0.2)
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
