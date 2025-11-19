from time import sleep

from random import randint

import paho.mqtt.client as mqtt
import vlc
import wave
import sys
import json
import os

mq_ip = "192.168.5.11"
deviceId = "cantina_band"
language = "de"
current_video = -1
playback_finished = False

_jsonData = {
    "id": deviceId,
}

instance = vlc.Instance()
player = instance.media_list_player_new()
player.get_media_player().toggle_fullscreen()


def play_movie(file):
    print("Playing movie: /var/lib/outposts/%s" % file)
    list = instance.media_list_new()
    list.add_media("/var/lib/outposts/%s" % file)
    #list.add_media("%s" % file)
    player.set_media_list(list)
    player.play()
    player.next()

### Game events ###
def on_event(event):
    if event == "Mystery solved":
        play_movie("cantina_band.mp3") 
    if event == "Self destruct":
        play_movie("diva_dance.mp3")        
    if event == "AI won":
        sleep(15)
        play_movie("imperial_march.mp3")
    if event == "Core removed":
        sleep(22)
        play_movie("space_odyssey.mp3")


### Global commands ###
def on_started():
    pass

def on_stopped():
    pass

def on_language_change(lang):
    global language
    if lang == "english":
        language = "en"
    elif lang == "deutsch":
        language = "de"
    
def sendUpdate():
    jsonData = _jsonData
    
    jsonData["game_state"] = "ALWAYS_ON"
    jsonData["state"] = "READY"
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
    client.subscribe("ToDevice/Instructions")
    client.publish("ToHost", json.dumps(jsonData))
    client.publish("FromDevice/%s" % deviceId, json.dumps(_jsonData))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global current_video
    print(msg.topic)
    print(msg.payload)
    payload = json.loads(msg.payload.decode('utf-8'))

    if msg.topic == "ToDevice/All":
        if 'gameState' in payload:
            gameState = payload["gameState"]
            if gameState == "STARTED":
                on_started()
            if gameState == "STOPPED":
                on_stopped()
            if gameState == "RESET":
                on_reset()
        if 'event' in payload:
            on_event(payload["event"])
        if 'language' in payload:
            on_language_change(payload["language"])
            
    if msg.topic == "ToDevice/Instructions":
        if 'cantina_movie' in payload:
            movie = payload["cantina_movie"]
            print("Request to play movie: %s" % movie)
            play_movie(movie + "_" + language + ".mp4")

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
sendUpdate()

print("starting message queue.")
mqttc.loop_start()

play_movie("background.mp4")

try:
    while True:
        position = player.get_media_player().get_position()
        #print(position)
        if position > 0.99:
            #print("PAUSING")
            #player.set_pause(1)

            play_movie("background.mp4")

        sleep(0.1)
        
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
