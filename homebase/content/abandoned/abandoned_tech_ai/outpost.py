import paho.mqtt.client as mqtt
import json
import gpiozero
import board
import neopixel
import RPi.GPIO as GPIO
from random import randint
from time import sleep
from threading import Thread

from time import sleep
from effects import Effects

deviceId = "abandoned_tech_ai"
demo = True
mq_ip = "192.168.178.11"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"

effects = Effects(led_count=150, pin=board.D18)
effects.start_pulse()

_jsonData = {
    "id": deviceId,
}

def sendUpdate():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))
    jsonData = _jsonData
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
        effects.fill((255, 0, 0))
        effects.start_pulse()

    if event == "Power up":
        effects.start_transition()

    if event == "All devices powered":
        effects.start_hunt()

    if event == "Easy ending":
        effects.trigger_easy_ending()
    
    if event == "Hard ending":
        effects.trigger_hard_ending()
    
    if event == "Core removed":
        sleep(1)
        effects.off(color = (255, 0, 0))
        effects.wipe(color = (255, 0, 0), transition_period=100, target_brightness=1)
        effects.wipe(color = (255, 0, 0), transition_period=2000, target_brightness=0)
        effects.off()
    

### Global commands ###
def on_started():
    effects.fill((255, 0, 0))
    effects.start_pulse()

def on_stopped():
    pass

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    

### Puzzle commands ###
def on_solved(client):
    pass

def on_reset(client):
    global _puzzleState
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

def random_transition():
    sleep(randint(5, 15))
    x = randint(0, 4)
    if ( x == 0):
        on_event("Power up")
    if ( x == 1):
        on_event("All devices powered")
    if ( x == 2):
        on_event("Hard ending")
    if ( x == 3):
        on_event("Easy ending")
    if (x == 4):
        on_event("Self destruction activated")

    t2 = Thread(target = random_transition)
    t2.start()


mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

connect(mqttc)

print("starting message queue.")
mqttc.loop_start()

effects.show_random_segments()
if demo:
    t2 = Thread(target = random_transition)
    t2.start()

while True:
    effects.next_iteration()
    if _gameState == "STOPPED":
        # Always be ready
        pass 
    sleep(0.02)

