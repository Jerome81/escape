import RPi.GPIO as GPIO
from time import sleep


# initialize door
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)


def close_drawer():
    GPIO.setup(12, GPIO.LOW)
    GPIO.setup(16, GPIO.LOW)
    print("Close drawer")

def open_drawer():
    GPIO.setup(12, GPIO.HIGH)
    GPIO.setup(16, GPIO.HIGH)
    print("Open drawer")

close_drawer()
sleep(5)
open_drawer()

