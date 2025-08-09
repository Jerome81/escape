import os
import paho.mqtt.client as mqtt
import serial
import time
from time import sleep
from adafruit_servokit import ServoKit
import json
import RPi.GPIO as GPIO



deviceId = "abandoned_tech_pressure"

mq_ip = "192.168.5.11"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"
_solution = [9, 2, 8, 7]
_currentData = [ 0,0,0,0 ]
_solved = False
_pressureCorrect = False


sensor_vals = [ 
    [ 1000, 330, 310, 285, 230, 185, 140, 80, 40, 10, -10 ], 
    [ 1000, 260, 210, 180, 150, 130, 100, 70, 40, 15, -10 ], 
    [ 1000, 560, 500, 430, 290, 230, 180, 100, 50, 15, -10 ], 
    [ 1000, 560, 520, 480, 380, 270, 180, 80, 40, 15, -10 ]
]

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}

kit = ServoKit(channels=16)
kit.servo[0].actuation_range = 11
kit.servo[1].actuation_range = 12  # Don't ask me why.
kit.servo[2].actuation_range = 11
kit.servo[3].actuation_range = 11

# initialize cartridge door
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)

def light_on():
    GPIO.setup(16, GPIO.LOW)
    print("Recycler light on")

def light_off():
    GPIO.setup(16, GPIO.HIGH)
    print("Recycler light off")

def find_pressure(v, sensor):
    for i in range(0, 10):
        if v < sensor[i] and v > sensor[i + 1]:
            return i


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
        if v != None:
            if _currentData[i] != 10 - v:
                has_changes = True
                _currentData[i] = 10 - v
                kit.servo[i].angle = v
    if has_changes:
        print(_currentData)
        if (_currentData == _solution):
            on_solved(mqttc)
        else:
            on_unsolved(mqttc)
        sendUpdate()

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
    global _solved
    if event == "All devices powered":
        on_activate()
    if event == "Recycling complete":
        _solved = True
        for i in range(0, 4):
            kit.servo[i].angle = 0



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
    global _pressureCorrect
    _puzzleState = "SOLVED"
    _pressureCorrect = True
    sendUpdate()
    jsonData = {
        "event": "Pressure correct"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))

def on_unsolved(client):
    global _puzzleState
    global _pressureCorrect
    _puzzleState = "ACTIVE"
    sendUpdate()
    if _pressureCorrect:
        _pressureCorrect = False    
        jsonData = {
            "event": "Pressure incorrect"
        }
        client.publish("ToDevice/All", json.dumps(jsonData))

def on_reset(client):
    global _puzzleState
    global _currentData
    global _solved
    _puzzleState = "RESET"
    light_off()
    _solved = False
    sendUpdate()
    jsonData = {
        "event": "Pressure incorrect"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))

def on_activate():
    global _puzzleState
    _puzzleState = "ACTIVE"
    light_on()
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

light_off()
sendUpdate()

errors_in_a_row = 0

try:
    ser = None
    while True:
    
        if _serial_connected == False:
            ser = connect_serial()
        
        if _serial_connected == False:
            sleep(5)
        else:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').rstrip()
                    print(line)
                    errors_in_a_row = 0
                except Exception as x:
                    print('An exception occurred: {}'.format(x))
                    errors_in_a_row = errors_in_a_row + 1
                    if errors_in_a_row == 5:
                        _currentData = ('5 exceptions in a row, contact Jerome: {}'.format(x))
                        sendUpdate()

                if _gameState == "STARTED":
                    if _puzzleState == "ACTIVE" or _puzzleState == "SOLVED":
                        if not _solved:
                            # Only update if the cartridge hasn't been produced.
                            # puzzleState is whether the current solution is correct. _solved is whether the cartridge was produced.
                            update_servos(line)
            sleep(0.1)

except Exception as e:
    s = ('An exception occurred: {}'.format(e))
    _currentData = s
    sendUpdate()
    print(s)
    print("Cleaning up")
