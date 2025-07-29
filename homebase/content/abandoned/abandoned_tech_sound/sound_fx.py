from time import sleep
from threading import Thread
from random import randint

import paho.mqtt.client as mqtt
import pyaudio
import wave
import sys
import json
import os

CHUNK = 1024

mq_ip = "192.168.5.11"
deviceId = "abandoned_tech_soundfx"

random_sounds = 3
random_min_wait = 30 # seconds
random_max_wait = 120 # seconds
_currently_playing = False
_gameState = "STOPPED"
_dock_door_unlocked = False
_language = "de"

_jsonData = {
    "id": deviceId,
}

def play_sound(file):
    global _currently_playing
    _currently_playing = True
    os.system("mpg321 %s" % file)
    _currently_playing = False

def play_random_sound():
    sleep_time = randint(random_min_wait, random_max_wait)
    print("Next random sound in %s seconds" % sleep_time)
    sleep(sleep_time)
    while _currently_playing:
        sleep(0.3)
    play_sound("random_%s.mp3" % randint(1, random_sounds))
    t2 = Thread(target = play_random_sound)
    t2.start()

def intruder_alert():

    while _currently_playing:
        sleep(0.3)
    play_sound("alarm_%s.mp3" % _language)    
    sleep_time = 15
    sleep(sleep_time)
    if not _dock_door_unlocked:
        intruder_alert_thread = Thread(target = intruder_alert)
        intruder_alert_thread.start()


### Game events ###
def on_event(event):
    global _dock_door_unlocked

    if event == "Intruder alert":
        play_sound("intruder_detected_%s.mp3" % _language)
        sleep(1)
        intruder_alert_thread.start()

    if event == "Ripplis hint":
        play_sound("rippli_hint_%s.mp3" % _language)    

    if event == "AI warning":
        play_sound("ai_warning_%s.mp3" % _language)

    if event == "ISS Riddle intervention":
        intruder_alert_thread.do_run = False
        play_sound("iss_riddle_help_%s.mp3" % _language)
        jsonData = {
            "command": "SOLVED"
        }
        mqttc.publish("ToDevice/abandoned_dock_door", json.dumps(jsonData))        	
        

    if event == "Dock door unlocked":
        intruder_alert_thread.do_run = False
        _dock_door_unlocked = True
        t2.start()

    if event == "All devices powered":
        play_sound("stromkreis_2.mp3")

    if event == "Power up":
        play_sound("stromkreis_1.mp3")

    if event == "Self destruct":
        play_sound("explosion_2.mp3")
        play_sound("self_destruct.mp3")

    if event == "Self destruction activated":
        play_sound("nooooo.mp3")

    if event == "Power down":
        play_sound("shutdown_server.mp3")

    if event == "Crew door open":
        play_sound("doors.mp3")

    if event == "Replicator ring production started" or event == "Replicator pyrometer production started" or event == "Replicator bubbles production started":
        play_sound("replicator.mp3")

    if event == "Joystick done":
        play_sound("doors.mp3")

    if event == "Cockpit door open":
        play_sound("doors.mp3")

    if event == "Cockpit door open":
        play_sound("keypad_approved.mp3")
    
    if event == "Access granted":
        play_sound("keypad_approved.mp3")



### Global commands ###
def on_started():
    pass

def on_stopped():
    pass

def on_language_change(language):
    global _language
    if language == "english":
         _language = "en"
    if language == "deutsch":
         _language = "de"
    print("changed language to %s." % language)
    
def sendUpdate():
    jsonData = _jsonData
    
    jsonData["game_state"] = _gameState
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))


### Puzzle commands ###
def on_solved(client):
    pass


def on_reset():
    pass

def on_activate():
    pass


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
            sendUpdate()
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

t2 = Thread(target = play_random_sound)
intruder_alert_thread = Thread(target = intruder_alert)

while True:
    sleep(0.5)