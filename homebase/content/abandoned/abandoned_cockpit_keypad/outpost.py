import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
import os

from time import sleep

mq_ip = "192.168.5.11"
deviceId = "abandoned_cockpit_keypad"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"
_solution = "40925"
_currentData = ""

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}

rowPins = [29, 31, 33, 35]
columnPins = [36, 38, 40]

keypad = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["*", "0", "#"]    
]

GPIO.setmode(GPIO.BOARD)

for pin in rowPins:
    GPIO.setup(pin, GPIO.OUT)

for pin in columnPins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def sendUpdate():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except e:
        print(e)

    jsonData = _jsonData
    jsonData["input"] = (_currentData)
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = ("%s - %s" % (_gameState, cpu_temp))
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))


### Game events ###
def on_event(event):
    if event == "Data inserted to send":
        on_activate()


### Global commands ###
def on_started():
    sendUpdate()

def on_stopped():
    sendUpdate()

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    

### Puzzle commands ###
def on_solved(client):
    global _puzzleState
    _puzzleState = "SOLVED"
    sendUpdate()
    jsonData = {
        "event": "Computer unlocked"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))

def on_reset():
    global _puzzleState
    _currentData = ""
    _puzzleState = "INACTIVE"
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
    sendUpdate()


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

lastInput = ""

try:
    while True:
        
        if _gameState == "STOPPED":
            # Always be ready
            sleep(0.1)
            continue
        
        if _puzzleState == "ACTIVE":
            
            if _puzzleState == "SOLVED":
                break
            
            row = 0
            for pinRow in rowPins:
                col = 0
                GPIO.output(pinRow, GPIO.HIGH)
                if (GPIO.input(pinRow) == 1):
                    for pinCol in columnPins:
                        if GPIO.input(pinCol) == 1:
                            key = keypad[row][col]
                            print("Row: %s - Col: %s ---> %s" % (row, col, key))
                            if key != lastInput:  # Prevent auto repeat
                                lastInput = key
                                _currentData = _currentData + key
                                _currentData = _currentData[-len(_solution):]  # Only as many characters as in the solution
                                print(_currentData)
                                sendUpdate()
                            if _currentData == _solution:
                                on_solved(mqttc)
                        col = col + 1
                GPIO.output(pinRow, GPIO.LOW)
                row = row + 1

                    
        else:
            sleep(1)
        
        
        sleep(0.05)
except Exception as e:
    print('An exception occurred: {}'.format(e))
finally:
    GPIO.cleanup()
