import paho.mqtt.client as mqtt
import json
import os
import gpiozero
import board
import neopixel
from random import shuffle

from time import sleep

deviceId = "abandoned_cockpit_joystick"

mq_ip = "192.168.178.11"

# Blue, Yellow, Red, Yellow, Green
_solution = ["W", "N", "S", "N", "E"]

_gameState = "STOPPED"
_puzzleState = "INACTIVE"

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}

_currentData = ["", "", "", "", ""]

LEDS = 48
light = neopixel.NeoPixel(board.D18, LEDS, brightness = 1, auto_write = False)
light.fill((255, 0, 0))
light.show()
_current_pixel = 0
_segment = 0
_north = False
_south = False
_east = False
_west = False


n = gpiozero.Button(24, hold_time = 0.1, bounce_time = 0.2)
n.when_pressed = lambda: west(True)
n.when_released = lambda: west(False)

s = gpiozero.Button(22, hold_time = 0.1, bounce_time = 0.2)
s.when_pressed = lambda: east(True)
s.when_released = lambda: east(False)

e = gpiozero.Button(25, hold_time = 0.1, bounce_time = 0.2)
e.when_pressed = lambda: north(True)
e.when_released = lambda: north(False)

w = gpiozero.Button(23, hold_time = 0.1, bounce_time = 0.2)
w.when_pressed = lambda: south(True)
w.when_released = lambda: south(False)

def north(is_set):
    global _north
    _north = is_set

def south(is_set):
    global _south
    _south = is_set

def east(is_set):
    global _east
    _east = is_set

def west(is_set):
    global _west
    _west = is_set

def diff_pixel(current_pixel, amount):
    pixel = current_pixel + amount
    if pixel > LEDS - 1:
        return pixel - LEDS
    if pixel < 0:
        return pixel
    return pixel

def move_segment():
    global _current_pixel
    global _segment
    global _north
    global _south
    global _east
    global _west
    _current_pixel = _current_pixel + 1
    if _current_pixel > LEDS - 1:
        _current_pixel = 0
    light[_current_pixel] = (0, 10, 20)
    light[diff_pixel(_current_pixel, -1)] = (0, 51, 102)
    light[diff_pixel(_current_pixel, -2)] = (51, 102, 204)
    light[diff_pixel(_current_pixel, -3)] = (0, 153, 255)
    light[diff_pixel(_current_pixel, -4)] = (0, 153, 255)
    light[diff_pixel(_current_pixel, -5)] = (0, 153, 255)
    light[diff_pixel(_current_pixel, -6)] = (0, 153, 255)
    light[diff_pixel(_current_pixel, -7)] = (0, 153, 255)
    light[diff_pixel(_current_pixel, -8)] = (0, 153, 255)
    light[diff_pixel(_current_pixel, -9)] = (0, 153, 255)
    light[diff_pixel(_current_pixel, -10)] = (51, 102, 204)
    light[diff_pixel(_current_pixel, -11)] = (0, 51, 102)
    light[diff_pixel(_current_pixel, -12)] = (0, 10, 20)
    light[diff_pixel(_current_pixel, -13)] = (0, 0, 0)
    light.show()
    if _current_pixel < 7 or _current_pixel > 42:
        if _segment != "S":
            _segment = "S"
            _north = False
            _south = False
            _west = False
            _east = False
        return
    if _current_pixel < 19 and _current_pixel > 6:
        if _segment != "W":
            _segment = "W"
            _north = False
            _south = False
            _west = False
            _east = False
        return
    if _current_pixel < 31 and _current_pixel > 18:
        if _segment != "N":
            _segment = "N"
            _north = False
            _south = False
            _west = False
            _east = False
        return
    if _current_pixel < 43 and _current_pixel > 30:
        if _segment != "E":
            _segment = "E"
            _north = False
            _south = False
            _west = False
            _east = False
        return

def light_up(color, start):
    for i in range(0, 12):
        light[diff_pixel(start, i)] = color
    
    light.show()

def light_up_segment():
    color = ((255, 255, 0))
    start = 43
    if _segment == "N":
        color = ((255, 255, 0))
        start = 19
    if _segment == "E":
        color = ((0, 255, 0))
        start = 31
    if _segment == "S":
        color = ((255, 0, 0))
    if _segment == "W":
        color = ((0, 0, 255))
        start = 7
    
    light_up(color, start)
    sleep(0.5)
    light_up((0, 0, 0), start)

    
def fade_out():
    light.fill((255, 255, 0))
    colors = [(255, 255, 102), (204, 204, 0), (102, 102, 0), (20, 20, 0), (0, 0, 0) ]
    for color in colors:
        leds = list(range(0, 48))
        shuffle(leds)
        while(len(leds) > 0):
            light[leds.pop(0)] = color
            light.show()
            sleep(0.005)

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


### Game events ###
def on_event(event):
    if event == "Access granted":
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
    fade_out()
    jsonData = {
        "event": "Joystick done"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))


def on_reset():
    global _puzzleState
    global _currentData
    _puzzleState = "ACTIVE"  # Always active
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
            light.fill((0, 0, 0))
            light.show()
            disconnected = False
        except Exception as e:
            print('An exception occured: {}'.format(e))
            sleep(5)

def getValue():
    selection = ""
    if _segment == "N" and _north:
        return "N"
    if _segment == "S" and _south:
        return "S"
    if _segment == "W" and _west:
        return "W"
    if _segment == "E" and _east:
        return "E"
    
    return ""

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

connect(mqttc)

print("starting message queue.")
mqttc.loop_start()

_last_value = ""
sendUpdate()

try:
    while True:
        
        if _gameState == "STARTED" and _puzzleState == "ACTIVE":
            move_segment()
            current_value = getValue()
            if current_value != _last_value:
                _last_value = current_value
                if current_value != "":
                    _currentData.pop(0)
                    _currentData.append(current_value)
                    light_up_segment()
                    sendUpdate()
                    if _currentData == _solution:
                        on_solved(mqttc)
                        print("You've done it! %s" % _currentData)
        sleep(0.05)
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
