
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
import gpiozero

from random import randint
from time import sleep
from mfrc522 import SimpleMFRC522


mq_ip = "192.168.178.11"
deviceId = "abandoned_dock_door"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"
_solution = [564472578780]
_currentData = ""


red = gpiozero.LED(17)
green = gpiozero.LED(27)

red.on()
green.on()

# initialize door
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}


def lock_door():
    GPIO.setup(12, GPIO.LOW)
    print("Door locked")

def unlock_door():
    GPIO.setup(12, GPIO.HIGH)
    print("Door unlocked")

def sendUpdate():
    jsonData = _jsonData
    
    jsonData["input"] = _currentData
    
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = _gameState
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))
    
 
def led_state():
    if _puzzleState == "ACTIVE":
        red.off()
        green.on()
        return
    if _puzzleState == "INACTIVE":
        red.on()
        green.off()
        return
        
    if _puzzleState == "SOLVED":
        red.off()
        green.off()
        return


### Game events ###
def on_event(event):
    if  event == "Dock keypad solved":
        on_activate()

### Global commands ###
def on_started():
    led_state()

def on_stopped():
    green.off()
    red.off()

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    

### Puzzle commands ###
def on_solved(client):
    global _puzzleState
    _puzzleState = "SOLVED"
    led_state()
    sendUpdate()
    jsonData = {
        "event": "Dock door unlocked"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))
    unlock_door()

def on_reset():
    global _puzzleState
    _puzzleState = "INACTIVE"
    _currentData = ""
    lock_door()
    led_state()
    sendUpdate()

def on_activate():
    global _puzzleState
    _puzzleState = "ACTIVE"
    led_state()
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

reader = SimpleMFRC522()
lastRead = None

green.off()
red.off()
lock_door()

try:
    while True:
        print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

        if _gameState == "STOPPED":
            # Always be ready
            pass 
        
        if _puzzleState == "ACTIVE":
            id = reader.read_id_no_block()
            
            if _puzzleState == "SOLVED":
                break

            # After each successful read, there is a None read.
            if id == None:
                if lastRead != None:
                    lastRead = None
                    continue
            
            lastRead == id

            if id != _currentData:
                _currentData = id
                sendUpdate()
                print(_currentData)
                print(_currentData in _solution)
                if _currentData in _solution:
                    print("solved")
                    on_solved(mqttc)
        else:
            sleep(1)
        
        
        sleep(0.2)
except Exception as e:
    print('An exception occurred: {}'.format(e))
finally:
    GPIO.cleanup
        
   
    