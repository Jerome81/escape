import subprocess
from signal import pause
from gpiozero import Button
import requests
import time

subprocess.Popen(['flask', '--app', 'voteometer', 'run', '-p', '5002', '--host=0.0.0.0'])

def button_pressed(number):
    return lambda: requests.get("http://127.0.0.1:5002/vote/%s" % number)

button1 = Button(2, pull_up = True, bounce_time = 0.1)
button2 = Button(3, pull_up = True, bounce_time = 0.1)
button3 = Button(5, pull_up = True, bounce_time = 0.1)
button4 = Button(13, pull_up = True, bounce_time = 0.1)


button1.when_released = button_pressed(1)
button2.when_released = button_pressed(2)
button3.when_released = button_pressed(3)
button4.when_released = button_pressed(4)

while(True):
    time.sleep(0.5)