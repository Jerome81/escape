import RPi.GPIO as GPIO
import time

import paho.mqtt.client as mqtt
import json
import gpiozero
import board
import neopixel
import traceback
from random import randint

from time import sleep
from datetime import datetime, timedelta
from effects import Effects


TRIGGER_1 = 15
ECHO_1 = 14

location = 0
has_sensor = True

mq_ip = "192.168.5.12"
LEDS = 300
deviceId = "passageway_%s" % location

effects = Effects(led_count=LEDS, pin=board.D18)

_jsonData = {
    "id": deviceId,
    "description": "Lighting %s in passageway" % location,
}

NO_CONNECTION_COLOR = ((0, 0, 130))
WHITEISH = ((50, 255, 50))
GREEN = ((0, 255, 0))
RED = ((255, 0, 0))

effects.just_light(RED)

_current_animation = "pulse"
_last_animation = None
_trigger_deactivated_until = None

### Passageway Events ###
def turn_on():
    global _current_animation
    sleep(location * 0.5)
    effects.wipe(GREEN, target_brightness=0.7, transition_period=1000)
    _current_animation = "pulse"

def turn_off():
    global _current_animation
    _current_animation = ""
    sleep((5 - location) * 0.5)
    effects.wipe((0, 0, 0), target_brightness=0, transition_period=1000)

def get_distance(triggerPin, echoPin):
    if has_sensor:
        i = 0
        GPIO.output(triggerPin, 0)
        sleep(2E-6)
        GPIO.output(triggerPin, 1)
        sleep(10E-6)

        while GPIO.input(echoPin) == 0 and i < 100000:
                i = i + 1
        pulse_start = time.time()
        if i > 99999:
             return 1000
        while GPIO.input(echoPin) == 1:
                pass
        pulse_end = time.time()

        pulse_duration = (pulse_end-pulse_start)
        return (pulse_duration*34444/2)
    else:
        return 9999


### Message Queue Events ###

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    jsonData = _jsonData
    jsonData["status"] = "Connected"

    client.subscribe("Lighting/%s" % deviceId)
    client.subscribe("Lighting/All")
    effects.morph(NO_CONNECTION_COLOR, GREEN, target_brightness = 0.7)
    effects.start_pulse()


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global _last_animation
    global _current_animation
    print(msg.topic)
    print(msg.payload)
    payload = msg.payload.decode('utf-8')

    if msg.topic == "Lighting/All":
        if payload == "ON":
            turn_on()
        if payload == "OFF":
            turn_off()
        if payload == "enter":
            #if _last_animation is None:
            effects.start_enter(location)
        if payload == "leave":
            if _last_animation is None:
                effects.start_leave(location)
        if payload == "rain":
            effects.start_rain()
        if payload == "pulse":
            effects.start_pulse()
        if payload == "red alert":
            effects.start_red_alert()
        if payload == "broken":
            effects.start_broken()

    if msg.topic == "Lighting/%s" % deviceId:
        if 'command' in payload:
            command = payload["command"]
            if command == "pulse":
                _current_animation = "pulse"



_connected = False
_next_connection_try = None
_next_connection_delay = timedelta(seconds=10)

def connect(client):
    global _next_connection_try
    global _connected
    if _next_connection_try is None or _next_connection_try < datetime.now():
        _next_connection_try = datetime.now() + _next_connection_delay
        try:
            client.connect(mq_ip, 1883, 60)
            client.loop_start()
            effects.fill((255, 255, 0))
            sleep(0.5)
            _connected = True
        except Exception as e:
            print('An exception occured: {}'.format(e))

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

effects.start_pulse()

GPIO.setup(TRIGGER_1, GPIO.OUT)
GPIO.setup(ECHO_1, GPIO.IN)

counter = 0
try:
    while True:
        if not _connected:
            connect(mqttc)
        effects.next_iteration()
        if (counter % 5 == 0):
            counter = 0
            distance = get_distance(TRIGGER_1, ECHO_1)
            if distance < 100:
                if _trigger_deactivated_until is None:
                    _trigger_deactivated_until = datetime.now() + timedelta(seconds=2)
                    mqttc.publish("Lighting/All", "enter")
                else:
                    if _trigger_deactivated_until < datetime.now():
                        _trigger_deactivated_until = datetime.now() + timedelta(seconds=2)
            else:
                if _trigger_deactivated_until is not None:
                    if _trigger_deactivated_until > datetime.now():
                        _trigger_deactivated_until = None

        counter = counter + 1
        sleep(0.05)

except Exception as e:
    print('An exception occurred: {}'.format(e))
    print(traceback.format_exc())
    print("Cleaning up")
    GPIO.cleanup()