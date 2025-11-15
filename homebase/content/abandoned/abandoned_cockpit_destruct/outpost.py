import paho.mqtt.client as mqtt
import json
import gpiozero
import board
import neopixel
import RPi.GPIO as GPIO
import os

from time import sleep

deviceId = "abandoned_cockpit_destruct"

mq_ip = "192.168.5.11"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"

_destructor = False
_safety = False

lightstrip = neopixel.NeoPixel(board.D18, 7, brightness = 1)
lightstrip.fill((255, 0, 0))

destructor = gpiozero.Button(14, hold_time = 0.1, bounce_time = 0.2)
destructor.when_pressed = lambda: on_solved()

safety = gpiozero.Button(15, hold_time = 0.1, bounce_time = 0.2)
safety.when_pressed = lambda: safety_deactivate()
safety.when_released = lambda: safety_activate()

# initialize door
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

_jsonData = {
    "id": deviceId,
    "description": "Lösung: true / true",
}

def safety_deactivate():
    global _safety
    _safety = True
    if _puzzleState == "ACTIVE":
        unlock_door()
        lightstrip.fill((0, 255, 0))
        jsonData = {
            "event": "Self destruction safety deactivated"
        }
        mqttc.publish("ToDevice/All", json.dumps(jsonData))
        sendUpdate()

def safety_activate():
    global _safety
    lightstrip.fill((255, 0, 0))
    _safety = False
    jsonData = {
        "event": "Self destruction safety activated"
    }
    mqttc.publish("ToDevice/All", json.dumps(jsonData))
    sendUpdate()

def lock_door():
    GPIO.setup(12, GPIO.LOW)
    print("Door locked")

def unlock_door():
    GPIO.setup(12, GPIO.HIGH)
    print("Door unlocked")

def sendUpdate():
    print("Game is: %s - Puzzle is: %s - Data: %s / %s" % (_gameState, _puzzleState, _safety, _destructor))
    input = ("%s / %s" % (_safety, _destructor))
    jsonData = _jsonData
    jsonData["input"] = input
    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except Exception as e:
        print(e)

    jsonData["state"] = _puzzleState
    jsonData["game_state"] = ("%s - %s" % (_gameState, cpu_temp))
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))
    

### Game events ###
def on_event(event):
    if event == "Self destruction activated":
        on_activate()

### Global commands ###
def on_started():
    pass

def on_stopped():
    pass

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    

### Puzzle commands ###
def on_solved():
    global _puzzleState
    global _destructor
    if _safety == True and _puzzleState == "ACTIVE":        
        _destructor = True
        _puzzleState = "SOLVED"            
        sendUpdate()
        jsonData = {
            "event": "Self destruct"
        }
        mqttc.publish("ToDevice/All", json.dumps(jsonData))

def on_reset(client):
    global _puzzleState
    _puzzleState = "INACTIVE"
    sendUpdate()
    jsonData = {
        "event": "Undestruct spaceship"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))

def on_activate():
    global _puzzleState
    _puzzleState = "ACTIVE"
    if _safety:
        unlock_door()
        lightstrip.fill((0, 255, 0))
    else:
        lightstrip.fill((255, 255, 255))
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
lightstrip.fill((0, 0, 0))
try:
    while True:
        
        if _gameState == "STOPPED":
            # Always be ready
            pass 
       
        sleep(0.2)
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
