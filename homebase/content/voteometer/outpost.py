import subprocess
from signal import pause
from gpiozero import Button

subprocess.Popen(['flask', '--app', 'voteometer', 'run', '-p', '5002', '--host=0.0.0.0'])

def button_pressed(number):
    return lambda: requests.get("http://127.0.0.1:5002/vote/%s" % number)

button1 = Button(2)
button2 = Button(3)

button1.when_released = button_pressed(1)
button2.when_released = button_pressed(2)

pause