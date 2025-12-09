import paho.mqtt.client as mqtt
import serial
import os
from time import time
from time import sleep
import json

import gpiozero
import RPi.GPIO as GPIO

deviceId = "abandoned_crew_replicator"

mq_ip = "192.168.5.11"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"
_cartridge_number = 0
_drawer_open = False
_blueprint = ""
_production_completed_at = 0

_jsonData = {
    "id": deviceId,
    "description": ("Blprt: Pyrometer - Crtrdg: 2 - True" ),
}

_cartridges = {
    2: "Hexapolym",
    3: "Amorata",
    4: "Partynom"    
}

button1 = gpiozero.Button(18, hold_time = 0.1, bounce_time = 0.2)
button2 = gpiozero.Button(23, hold_time = 0.1, bounce_time = 0.2)
button3 = gpiozero.Button(24, hold_time = 0.1, bounce_time = 0.2)

# initialize door
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)

def close_drawer():
    global _drawer_open 
    _drawer_open = False
    GPIO.setup(12, GPIO.LOW)
    GPIO.setup(16, GPIO.LOW)

    print("Close drawer")

def open_drawer():
    global _drawer_open 
    _drawer_open = True
    GPIO.setup(12, GPIO.HIGH)
    GPIO.setup(16, GPIO.HIGH)
    print("Open drawer")


def sendUpdate():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except Exception as e:
        print(e)

    jsonData = _jsonData
    jsonData["input"] = ("Bprt: %s - Crtrdg: %s - %s" % (_blueprint, _cartridge_number, _drawer_open))
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = ("%s - %s" % (_gameState, cpu_temp))
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))

### Game events ###
def on_event(event):
    global _cartridges
    if event == "All devices powered":
        on_activate()
    try:
        if event == "Replicator ring production started":
            if 3 in _cartridges:
                _cartridges.pop(3)
            on_solved(mqttc)

        if event == "Replicator pyrometer production started":
            if 2 in _cartridges:
                _cartridges.pop(2)
            on_solved(mqttc)
            mqttc.publish("cmnd/sleeping_pods/Power", "on")

        if event == "Replicator bubbles production started":
            if 4 in _cartridges:
                _cartridges.pop(4)
            on_solved(mqttc)
    except Exception as e:
        print('An exception occurred: {}'.format(e))

def blueprint_inserted(event):
    global _blueprint
    _blueprint = event
    publish_event(event + " blueprint inserted")
    sendUpdate()

def blueprint_removed():
    global _blueprint
    _blueprint = ""
    publish_event("Blueprint removed")
    sendUpdate()

def cartridge_removed():
    print("Cartridge removed")
    sendUpdate()
    publish_event("No cartridge inserted")

def new_cartridge():
    print("Cartridge %s" % _cartridge_number)
    if _cartridge_number in _cartridges:
        sendUpdate()
        try:
            publish_event("%s inserted" % _cartridges[_cartridge_number])
        except Exception as e:
            print("No cartridge with number: %s" % _cartridge_number)


def publish_event(event):
    jsonData = {
        "event": event
    }
    mqttc.publish("ToDevice/All", json.dumps(jsonData))


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
    global _production_completed_at
    sleep(11)    
    publish_event(_blueprint + " produced")
    _production_completed_at = time()
    open_drawer()
    _puzzleState = "SOLVED"
    sendUpdate()


def on_unsolved(client):
    global _puzzleState
    _puzzleState = "ACTIVE"
    sendUpdate()
    
def on_reset(client):
    global _puzzleState
    global _cartridges
    global _blueprint
    global _cartridge_number
    _puzzleState = "RESET" 
    sendUpdate()
    _cartridges = {
        2: "Hexapolym",
        3: "Amorata",
        4: "Partynom"    
    }
    _cartridge_number = 0
    _blueprint = ""

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


def connect_serial():
    global _serial_connected
    global _currentData
    if _serial_connected:
        return
    
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
        ser.reset_input_buffer()
        _serial_connected = True
        return ser
    except Exception as e:
        s = ('An exception occurred: {}'.format(e))
        _currentData = s

def inserted(n):
    global _cartridge_number
    _cartridge_number = _cartridge_number + n
    print("Cartridge number: %s" % _cartridge_number)

def removed(n):
    global _cartridge_number
    _cartridge_number = _cartridge_number - n
    if _cartridge_number < 0:
        _cartridge_number = 0
    print("Cartridge number: %s" % _cartridge_number)


button1.when_pressed = lambda: inserted(1)
button1.when_released = lambda: removed(1)

button2.when_pressed = lambda: inserted(2)
button2.when_released = lambda: removed(2)

button3.when_pressed = lambda: inserted(4)
button3.when_released = lambda: removed(4)


mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

connect(mqttc)

_serial_connected = False

print("starting message queue.")
mqttc.loop_start()

close_drawer()
sendUpdate()

try:
    last_cartridge = _cartridge_number
    last_blueprint_insertion = 0
    ser = None
    while True:
        if _serial_connected == False:
            ser = connect_serial()
        
        if _serial_connected == False:
            sleep(5)
        else:
            if _gameState == "STARTED" and _puzzleState == "ACTIVE":
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').rstrip()
                    line = line.strip()
                    codeword = "Replikator: "
                    if line.startswith(codeword):
                        last_blueprint_insertion = time()
                        event = line[len(codeword)::]
                        if event != _blueprint:
                            blueprint_inserted(event)
                    if time() - last_blueprint_insertion > 2 and _blueprint != "":
                        blueprint_removed()
                sleep(0.05)
                if last_cartridge != _cartridge_number:
                    last_cartridge = _cartridge_number
                    if _cartridge_number == 0:
                        cartridge_removed()
                    else:
                        new_cartridge()
            else:
                if _production_completed_at > 0 and time() - _production_completed_at > 120:
                    _production_completed_at = 0
                    _blueprint = ""
                    _cartridge_number = 0
                    _puzzleState = "ACTIVE"
                    close_drawer()
                    publish_event("Replicator ready again")
                    sendUpdate()
                ser.reset_input_buffer()
                sleep(0.3)

except Exception as e:
    s = ('An exception occurred: {}'.format(e))
    _currentData = s
    sendUpdate()
    print(s)
    print("Cleaning up")