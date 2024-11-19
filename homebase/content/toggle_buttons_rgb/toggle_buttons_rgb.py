import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json

from time import sleep

deviceId = "abandoned_engineroom_circuit"

_gameState = "STOPPED"
_puzzleState = "ACTIVE"
_solution = [False, False, False, False, False, False, False, True ]
_currentData = []

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}

BUTTON = 0
RED = 1
GREEN = 2
BLUE = 3
SELECTED = 4

# The same pin is used for RED and GREEN, because red is not being used to save pins.
buttons = [
    [40, 37, 37, 35, False], # button, red, green, blue, InitiallySelected
    [38, 33, 33, 31, False],
    [36, 29, 29, 23, False],
    [32, 21, 21, 19, False],
    [26, 15, 15, 13, False],
    [24, 11, 11, 7, False],
    [22, 5, 5, 3, False],
    [18, 10, 10, 8, False],
]

GPIO.setmode(GPIO.BOARD)

def setButtonState(button, isSelected):
    if isSelected:
        GPIO.output(button[BLUE], 1)
    else:
        GPIO.output(button[BLUE], 0)


def sendPuzzleState():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

    jsonData = _jsonData
    jsonData["state"] = _puzzleState
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))

def sendUpdate():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

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
    

### Puzzle commands ###
def on_solved(client):
    global _puzzleState
    _puzzleState = "SOLVED"
    sendPuzzleState()
    jsonData = {
        "event": "Dock keypad solved"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))

def on_reset():
    global _puzzleState
    _currentData = ""
    sendUpdate()
    _puzzleState = "INACTIVE"
    sendPuzzleState()

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

lastButtonState = [] # contains the last known state of the button (i.e. is the user currently pressing it and holding it down?)
UP = 1
DOWN = 0

for button in buttons:
    GPIO.setup(button[BUTTON], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button[RED], GPIO.OUT)
    GPIO.setup(button[GREEN], GPIO.OUT)
    GPIO.setup(button[BLUE], GPIO.OUT)
    _currentData.append(button[SELECTED])
    setButtonState(button, button[SELECTED])
    lastButtonState.append(UP)


try:
    while True:
        
        if _gameState == "STOPPED":
            # Always be ready
            pass 
        
        if _puzzleState == "ACTIVE":
            i = 0
            for button in buttons:
                isUp = GPIO.input(button[BUTTON])
                if isUp != lastButtonState[i]:
                    lastButtonState[i] = isUp
                else:
                    i = i + 1
                    continue

                # Only act on button up.
                if lastButtonState[i] == UP:
                    print("Button %s action" % i)
                    _currentData[i] = not _currentData[i]
                    setButtonState(button, _currentData[i])
                    print(_currentData)
            
            i = i + 1
                    
        else:
            sleep(1)
        
        
        sleep(0.2)
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
    GPIO.cleanup()
