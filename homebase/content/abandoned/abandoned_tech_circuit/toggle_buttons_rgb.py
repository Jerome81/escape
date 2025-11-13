import os
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
from gpiozero import Button

#import pygame

import board
import neopixel

from time import sleep

mq_ip = "192.168.5.11"
deviceId = "abandoned_tech_circuit"

_gameState = "STOPPED"
_puzzleState = "ACTIVE"
_solution = [True, False, True, True, False, False, True, True ]
_currentData = []
_lastButtonState = [] # contains the last known state of the button (i.e. is the user currently pressing it and holding it down?)

lightstrip = neopixel.NeoPixel(board.D18, 250, brightness = 0.6, auto_write=False)
lightstrip.fill((255, 0, 0))
lightstrip.show()

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
# GPIO PINS
buttons = [
    [Button(24, bounce_time = 0.05), 15, 15, 14, False], # button, red, green, blue, InitiallySelected
    [Button(25, bounce_time = 0.05), 3, 3, 2, False],
    [Button(23, bounce_time = 0.05), 17, 17, 4, False],
    [Button(0, bounce_time = 0.05), 22, 22, 27, False],
    [Button(12, bounce_time = 0.05), 9, 9, 10, False],
    [Button(16, bounce_time = 0.05), 5, 5, 11, False],
    [Button(20, bounce_time = 0.05), 13, 13, 6, False],
    [Button(21, bounce_time = 0.05), 26, 26, 19, False], 
]

#pygame.init()

GPIO.setmode(GPIO.BCM)

def setButtonState(button, isSelected):
    if isSelected:
        print("High on: %s" % button[BLUE])
        GPIO.output(button[BLUE], 1)
    else:
        
        print("Low on: %s" % button[BLUE])
        GPIO.output(button[BLUE], 0)

def sendUpdate():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except Exception as e:
        print(e)

    jsonData = _jsonData
    jsonData["input"] = (_currentData)
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = ("%s - %s" % (_gameState, cpu_temp))
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))
    
def power_on_animation():
    lightstrip.brightness = 0.8
    color = (255, 255, 255)
    for i in range(len(lightstrip) - 1, -1, -1):
        lightstrip[i] = color
        if i < 106:
            color = (255, 255, 255)
            continue
        else:          
            lightstrip.show() 
            sleep(0.02)
    lightstrip.show() 

def power_off_animation():
    for i in range(0, len(lightstrip)):
        lightstrip[i] = (0, 0, 0)
        if i < 106:
            continue
        else:
            lightstrip.show()
            sleep(0.02)

def attract():
    if _puzzleState == "ACTIVE":
        w = [0.03, 1, 0.03, 0.5, 0.03, 0.1, 0.03, 0.03 ]
        for i in range(len(w)):
            lightstrip.brightness = i % 2
            lightstrip.show()
            sleep(w[i])
        lightstrip.brightness = 0.6
        lightstrip.show()

### Game events ###
def on_event(event):
    if event == "Power up":
        on_activate()

    if event == "Power down":
        on_reset()

    if event == "Attract":
        attract()

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
    _puzzleState = "SOLVED"
    for button in buttons:
        GPIO.output(button[BLUE], 0)
        GPIO.output(button[GREEN], 1)
    sendUpdate()
    jsonData = {
        "event": "All devices powered"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))
    for i in range(105):
        lightstrip[i] = (0, 255, 0)

    lightstrip.brightness = 0.3
    lightstrip.show()

def on_reset():
    global _puzzleState
    global _currentData
    global _lastButtonState
    _lastButtonState = []
    _currentData = []
    _puzzleState = "INACTIVE"
    sendUpdate()
    for button in buttons:
        GPIO.output(button[BLUE], 0)
        GPIO.output(button[GREEN], 0)
        setButtonState(button, button[SELECTED])
        _currentData.append(button[SELECTED])
        _lastButtonState.append(UP)
    power_off_animation()

def button_pressed(number):
    global _currentData
    if _puzzleState == "ACTIVE":
        print("Button %s action" % number)
        _currentData[number] = not _currentData[number]
        setButtonState(buttons[number], _currentData[number])
        print(_currentData)
        if _currentData == _solution:
            on_solved(mqttc)
    else:
        print("Button %s pressed but puzzle not active" % number)

def on_release(number):
    if number == 0:
        return lambda: button_pressed(0)
    if number == 1:
        return lambda: button_pressed(1)
    if number == 2:
        return lambda: button_pressed(2)
    if number == 3:
        return lambda: button_pressed(3)
    if number == 4:
        return lambda: button_pressed(4)
    if number == 5:
        return lambda: button_pressed(5)
    if number == 6:
        return lambda: button_pressed(6)
    if number == 7:
        return lambda: button_pressed(7)

def on_activate():
    global _puzzleState
    _puzzleState = "ACTIVE"
    sendUpdate()
    power_on_animation()


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
UP = 1
DOWN = 0

i = 0
for button in buttons:
    button[BUTTON].when_released = on_release(i)
    GPIO.setup(button[RED], GPIO.OUT)
    GPIO.setup(button[GREEN], GPIO.OUT)
    GPIO.setup(button[BLUE], GPIO.OUT)
    i = i + 1

on_reset()


try:
    while True:
                
        sleep(0.3)

except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
    GPIO.cleanup()
