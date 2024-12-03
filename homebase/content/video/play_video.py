from time import sleep
import vlc

instance = vlc.Instance()
list = instance.media_list_new()
video = vlc.Media("/var/lib/outposts/output.mp4")
list.add_media(video)
player = instance.media_list_player_new()
player.set_media_list(list)
player.get_media_player().toggle_fullscreen()

player.set_playback_mode(vlc.PlaybackMode(1)) # loop
player.play()


while True:
    sleep(0.5)
    pass