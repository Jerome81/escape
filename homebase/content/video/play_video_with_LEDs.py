import vlc
import RPi.GPIO as GPIO
import gpiozero
from time import sleep

instance = vlc.Instance()

def create_player(file):
    list = instance.media_list_new()
    video = vlc.Media(file)
    list.add_media(video)
    player = instance.media_list_player_new()
    player.set_media_list(list)
    player.get_media_player().toggle_fullscreen()
    player.set_playback_mode(vlc.PlaybackMode.loop)
    return player

LIGHT = 0
START = 1
END = 2

config = {
    [gpiozero.LED(4), 0.0, 0.9 ],
    [gpiozero.LED(17), 0.5, 0.8 ],
    [gpiozero.LED(27), 0.3, 0.6 ],
    [gpiozero.LED(22), 0.1, 0.4 ] 
}

player = create_player("/home/outpost/output.mp4")
player.play()

while True:
    while player.is_playing():
        sleep(0.1)
        position = player.get_media_player().get_position()
        for light in config:
            if position > light[START] and position < light[END]:
                light[LIGHT].on()
            else:
                if light[LIGHT].is_lit:
                    light[LIGHT].off()