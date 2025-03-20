
import smbus
import time
from time import sleep
import paho.mqtt.client as mqtt
import json
import gpiozero
import board
import neopixel

deviceId = "pressure"

mq_ip = "192.168.178.11"

_gameState = "STOPPED"
_puzzleState = "ACTIVE"
PRESSED = 0
UNPRESSED = 1

_solution = [3, 2, 1, 5]
_currentData = [0, 0, 0, 0]

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}


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
        if not button.is_pressed:
            return
        sleep(0.02)

def power_off_animation(): 
    for i in range(len(lightstrip) - 1, -1, -1):
        lightstrip[i] = (0, 0, 0)
        if button.is_pressed:
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

# Get I2C bus
bus = smbus.SMBus(1)
sensor_addresses = [0x23]
sensor_max_vals = [100]

def start_sensors(addresses):
    for sensor in addresses:
        # BH1715 address, 0x23(35)
        # Send power on command
        #		0x01(01)	Power On
        bus.write_byte(sensor, 0x01)

def read_sensors(addresses, max_vals):
    for sensor in addresses:
        # BH1715 address, 0x23(35)
        # Send continuous measurement command
        #		0x10(16)	Set Continuous high resolution mode, 1 lux resolution, Time = 120ms
        bus.write_byte(sensor, 0x10)

    time.sleep(0.5)

    vals = []
    i = 0
    for sensor in addresses:    
        # BH1715 address, 0x23(35)
        # Read data back, 2 bytes using General Calling
        # luminance MSB, luminance LSB
        data = bus.read_i2c_block_data (0x23, 2)

        # Convert the data
        luminance = (data[0] * 256 + data[1]) / 1.2
        vals.append(luminance * max_vals[i] / 100)
        i = i + 1
    
    return vals

start_sensors(sensor_addresses)

try:
    while True:
        
        if _gameState == "STOPPED":
            # Always be ready
            pass 
       
        print(read_sensors(sensor_addresses, sensor_max_vals))
        sleep(0.2)
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")

