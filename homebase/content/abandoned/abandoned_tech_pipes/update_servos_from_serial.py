import paho.mqtt.client as mqtt
import serial
import time
from time import sleep
from adafruit_servokit import ServoKit
import json


deviceId = "abandoned_tech_pressure"

mq_ip = "192.168.5.11"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"
_solution = [5, 1, 9, 3]
_currentData = [ 0,0,0,0 ]

sensor_vals = [
    [ 1000, 390, 360, 300, 270, 200, 140, 80, 40, 10, -10 ],
    [ 1000, 290, 220, 180, 150, 130, 100, 60, 30, 15, -10 ],
    [ 1000, 620, 580, 500, 420, 250, 180, 100, 50, 15, -10 ],
    [ 1000, 590, 550, 480, 380, 270, 180, 80, 40, 10, -10 ] ]

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}

kit = ServoKit(channels=16)
kit.servo[0].actuation_range = 11
kit.servo[1].actuation_range = 11
kit.servo[2].actuation_range = 11
kit.servo[3].actuation_range = 11

def find_pressure(v, sensor):
    for i in range(0, 10):
        if v < sensor[i] and v > sensor[i + 1]:
        return i
    return 11

def update_servos(line):
    global _currentData
    vals = line.split(",")
    if len(vals) < 4:
        print(line)
        print("Doesn't split into 4 tokens.")
        return
    
    has_changes = False
    for i in range(0, 4):
        v = find_pressure(int(vals[i]), sensor_vals[i])
        if _currentData[i] != v:
            has_changes = True
            _currentData[i] = v
            kit.servo[i].angle = v
    if has_changes:
        print(_currentData)
        if (_currentData == _solution):
            on_solved(mqttc)
        else:
            on_unsolved(mqttc)
        sendUpdate()

def sendUpdate():
    print("Game is: %s - Puzzle is: %s - Data: %s" % (_gameState, _puzzleState, _currentData))

    jsonData = _jsonData
    jsonData["input"] = _currentData
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = _gameState
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))

### Game events ###
def on_event(event):
    if event == "All devices powered":
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
    jsonData = {
        "event": "Pressure correct"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))

def on_unsolved(client):
    global _puzzleState
    _puzzleState = "ACTIVE"
    sendUpdate()
    jsonData = {
        "event": "Pressure incorrect"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))

def on_reset(client):
    global _puzzleState
    global _currentData
    _puzzleState = "RESET"  # Always active
    sendUpdate()
    jsonData = {
        "event": "Pressure incorrect"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))

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
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        ser.reset_input_buffer()
        _serial_connected = True
        return ser
    except Exception as e:
        s = ('An exception occurred: {}'.format(e))
        _currentData = s
        sendUpdate()

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

connect(mqttc)

_serial_connected = False

print("starting message queue.")
mqttc.loop_start()


try:
    ser = None
    
    while True:
        if _serial_connected == False:
            ser = connect_serial()
        
        if _serial_connected == False:
            sleep(5)
        else:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                update_servos(line)

            sleep(0.1)

except Exception as e:
    s = ('An exception occurred: {}'.format(e))
    _currentData = s
    sendUpdate()
    print(s)
    print("Cleaning up")
