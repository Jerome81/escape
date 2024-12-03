import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
import gpiozero
import board
import neopixel

from time import sleep

deviceId = "abandoned_engineroom_power"

_gameState = "STOPPED"
_puzzleState = "ACTIVE"
PRESSED = 0
UNPRESSED = 1

_solution = PRESSED
_currentData = UNPRESSED

lightstrip = neopixel.NeoPixel(board.D18, 100, brightness = 1)
lightstrip.fill((255, 0, 0))

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}

BUTTON_PIN = 14  #GPIO14
LED_PIN = 26  #GPIO26

light = gpiozero.LED(LED_PIN)
light.on()

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def sendPuzzleState():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

    jsonData = _jsonData
    jsonData["state"] = _puzzleState
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))

def sendUpdate():
    print("Game is: %s - Puzzle is: %s - Data: %s" % (_gameState, _puzzleState, _currentData))

    jsonData = _jsonData
    jsonData["input"] = _currentData
    jsonData["state"] = _puzzleState
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))
    

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
    

def power_on_animation():
    for i in range(len(lightstrip)):
        lightstrip[i] = (255, 255, 255)
        if GPIO.input(BUTTON_PIN) == 1:
            return
        sleep(0.02)

def power_off_animation(): 
    for i in range(len(lightstrip) - 1, -1, -1):
        lightstrip[i] = (0, 0, 0)
        if GPIO.input(BUTTON_PIN) == 0:
            return
        sleep(0.02)


### Puzzle commands ###
def on_solved(client):
    global _puzzleState
    power_on_animation()
    _puzzleState = "SOLVED"
    sendUpdate()
    light.off()
    jsonData = {
        "event": "Power up"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))


def on_reset(client):
    global _puzzleState
    global _currentData
    _puzzleState = "ACTIVE"  # Always active
    light.on()
    sendUpdate()
    jsonData = {
        "event": "Power down"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))
    power_off_animation()

def on_activate():
    global _puzzleState
    _puzzleState = "ACTIVE"
    sendPuzzleState()


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

   

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")
mqttc.connect("192.168.178.11", 1883, 60)

print("starting message queue.")
mqttc.loop_start()
UP = 1
DOWN = 0
lastState = UP

on_reset(mqttc)

try:
    while True:
        
        if _gameState == "STOPPED":
            # Always be ready
            pass 
    
        i = 0
        isUp = GPIO.input(BUTTON_PIN)
        if isUp != lastState:
            _currentData = isUp
            lastState = isUp
            if isUp:
                on_reset(mqttc)
            else:
                on_solved(mqttc)
        
        sleep(0.2)
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
    GPIO.cleanup()
