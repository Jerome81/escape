import os
import vlc

import paho.mqtt.client as mqtt
import json
import gpiozero
import RPi.GPIO as GPIO

from time import sleep

deviceId = "rippli"

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
    "de": [ "/var/lib/outposts/background.mp4", "/var/lib/outposts/video_0_de.mp4", "/var/lib/outposts/video_1_de.mp4", "/var/lib/outposts/video_2_de.mp4", "/var/lib/outposts/background.mp4" ],
    "en": [ "/var/lib/outposts/background.mp4", "/var/lib/outposts/video_0_en.mp4", "/var/lib/outposts/video_1_en.mp4", "/var/lib/outposts/video_2_en.mp4", "/var/lib/outposts/background.mp4" ]
}

instance = vlc.Instance()
player = instance.media_list_player_new()
player.get_media_player().toggle_fullscreen()
list = instance.media_list_new()
for video in playlists[language]:
    list.add_media(video)
player.set_media_list(list)

VIDEOS = list.count()


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
    #play("video_%s" % current_video)


next_button.when_pressed = lambda: on_next()
prev_button.when_pressed = lambda: on_prev()

#player.event_manager().event_attach(vlc.EventType.MediaListPlayerNextItemSet, video_finished)

player.play()
playback_finished = False

try:
    while True:
        position = player.get_media_player().get_position()
        #print(position)
        if position > 0.95:
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
