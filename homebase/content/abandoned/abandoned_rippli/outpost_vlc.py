import os
import vlc

import paho.mqtt.client as mqtt
import json
import gpiozero
import RPi.GPIO as GPIO

from time import sleep

deviceId = "helen_rippli"

mq_ip = "192.168.5.11"

_gameState = "STARTED"
_puzzleState = "ACTIVE"
_jsonData = {
    "id": deviceId,
    "description": ("Screen von %s" % deviceId),
}

next_button = gpiozero.Button(14, hold_time = 0.05, bounce_time = 0.1)
prev_button = gpiozero.Button(15, hold_time = 0.05, bounce_time = 0.1)
current_video = 0

show_next = False
show_prev = False
playback_finished = False

language = "de"
playlists = {
    "de": [ "/var/lib/outposts/helen_rippli_start_de.mp4", "/var/lib/outposts/helen_rippli_1_de.mp4", "/var/lib/outposts/helen_rippli_2_de.mp4", "/var/lib/outposts/helen_rippli_3_de.mp4", "/var/lib/outposts/end_de.mp4" ],
    "en": [ "/var/lib/outposts/helen_rippli_start_en.mp4", "/var/lib/outposts/helen_rippli_1_en.mp4", "/var/lib/outposts/helen_rippli_2_en.mp4", "/var/lib/outposts/helen_rippli_3_en.mp4", "/var/lib/outposts/end_en.mp4" ]
}

instance = vlc.Instance()
player = instance.media_list_player_new()
player.get_media_player().toggle_fullscreen()
list = instance.media_list_new()
for video in playlists[language]:
    list.add_media(video)
player.set_media_list(list)

VIDEOS = list.count()


def sendUpdate():

    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except Exception as e:
        print(e)

    jsonData = _jsonData
    jsonData["input"] = current_video
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = ("%s - %s" % (_gameState, cpu_temp))
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))

### Game events ###
def on_event(event):
    # I listen to no events
    pass


### Global commands ###
def on_started():
    on_activate()

def on_stopped():
    # Always active, do nothing
    pass

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    

### Puzzle commands ###
def on_solved():
    # Nothing to do here
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

def video_finished(event):
    global playback_finished
    print("VIDEO FINISHED")
    print(event)
    playback_finished = True

def on_next():
    global current_video
    global show_next
    print("next")
    current_video = current_video + 1
    print(current_video)
    if current_video >= VIDEOS:
        current_video = VIDEOS - 1
    else:
        show_next = True
    sendUpdate()
    #play("video_%s" % current_video)


def on_prev():  
    global current_video
    global show_prev
    print("prev")
    print(current_video)
    current_video = current_video - 1
    if current_video < 0:
        current_video = 0
    else:
        show_prev = True
    sendUpdate()
    #play("video_%s" % current_video)


next_button.when_pressed = lambda: on_next()
prev_button.when_pressed = lambda: on_prev()

#player.event_manager().event_attach(vlc.EventType.MediaListPlayerNextItemSet, video_finished)

player.play()
playback_finished = False
sendUpdate()

try:
    while True:
        position = player.get_media_player().get_position()
        #print(position)
        if position > 0.98:
            #print("PAUSING")
            player.set_pause(1)
        if show_next:
            print("Showing next: %s" % current_video)
            show_next = False
            player.play_item_at_index(current_video)
            playback_finished = False
            show_prev = False
        if show_prev:
            print("Showing previous")
            show_prev = False
            player.play()
            playback_finished = False
            player.previous()
        if playback_finished:
            print("Playback finished")
            playback_finished = False
            show_next = False
            show_prev = False
            media_state = player.get_state()
            vlc_playing = set([3, 4]) # 3 - Playing / 4 - Paused
            while media_state not in vlc_playing:
                media_state = player.get_state()
            print("Pausing video")
            player.pause()

        sleep(0.1)
        
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
    current_video = "ERROR"
    sendUpdate()
