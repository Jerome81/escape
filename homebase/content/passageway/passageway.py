import paho.mqtt.client as mqtt
import json
import gpiozero
import board
import neopixel

from gpiozero import DistanceSensor
from time import sleep

location = 1
mq_ip = "192.168.178.106"
LEDS = 100
deviceId = "passageway_%s" % location

lightstrip = neopixel.NeoPixel(board.D18, LEDS, brightness = 1)
lightstrip.fill((255, 0, 0))

_jsonData = {
    "id": deviceId,
    "description": "Lighting %s in passageway" % location,
}

_current_animation = "pulse"
_somebody_in_range = False



### Effects ###
def start_pulse():  
    _step = -0.05
    _brightness = 0.8

def pulse():

    global _brightness
    global _step

    lightstrip.brightness = _brightness
    _brightness = _brightness + _step
    if _brightness < 0.2 or _brightness > 0.8:
        _step = -_step

    sleep(0.05)

def wipe(color, transition_period = 2000, target_brightness = 1):
    steps = round(LEDS / 2)
    diff_brightness = target_brightness - lightstrip.brightness
    bright_step = diff_brightness / steps
    for i in range(0, steps):
            lightstrip.brightness = lightstrip.brightness + bright_step
            lightstrip[i] = color
            lightstrip[(LEDS - 1) - i] = color
            lightstrip.show()
            sleep((transition_period / 1000) / steps)

def morph(start_color, destination_color, steps = 50, transition_period = 2000, target_brightness = 1):

    red_start = start_color[0]
    green_start = start_color[1]
    blue_start = start_color[2]
    
    diff_brightness = target_brightness - lightstrip.brightness
    bright_step = diff_brightness / steps
    
    red = start_color[0] - destination_color[0]
    green = start_color[1] - destination_color[1]
    blue = start_color[2] - destination_color[2]

    red_increment = red / steps
    green_increment = green / steps
    blue_increment = blue / steps

    for i in range(0, steps):
        new_red = round(red_start - (red_increment * i))
        new_green = round(green_start - (green_increment * i))
        new_blue = round(blue_start - (blue_increment * i))
        lightstrip.fill((new_red, new_green, new_blue))
        lightstrip.brightness = lightstrip.brightness + bright_step
        sleep((transition_period / 1000) / steps)

def morph_to(destination_color):
     morph(lightstrip[0], (destination_color))


def next_iteration():
    if _somebody_in_range:
        pass
    else:
        if _current_animation == "pulse":
            pulse()


### Passageway Events ###
def turn_on():
    sleep((location - 1) * 0.5)
    wipe((0, 0, 100), target_brightness=1)

def turn_off():
    sleep((6 - location) * 0.5)
    wipe((0, 0, 0), target_brightness=0)

### Message Queue Events ###

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    jsonData = _jsonData
    jsonData["status"] = "Connected"

    client.subscribe("Lighting/%s" % deviceId)
    client.subscribe("Lighting/All")
    morph((255, 0, 0), (0, 0, 40), target_brightness = 0.4)
    lightstrip.show()


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic)
    print(msg.payload)
    payload = msg.payload.decode('utf-8')

    if msg.topic == "Lighting/All":
        if payload == "ON":
            turn_on()
        if payload == "OFF":
            turn_off()

    if msg.topic == "Lighting/%s" % deviceId:
        if 'command' in payload:
            command = payload["command"]
            if command == "pulse":
                _current_animation = "pulse"
   


_disconnected = True
def connect(client):
    global _disconnected
    while _disconnected:
        try:   
            client.connect(mq_ip, 1883, 60)
            client.loop_start()
            _disconnected = False
        except Exception as e:
            print('An exception occured: {}'.format(e))
            sleep(5)
            _disconnected = False

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

morph((255, 0, 0), (0, 0, 120))
start_pulse()

ultrasonic = DistanceSensor(echo=24, trigger=23)
while True:
    if _disconnected:
         connect(mqttc)
    next_iteration()
    print(ultrasonic.distance)
    sleep(0.05)