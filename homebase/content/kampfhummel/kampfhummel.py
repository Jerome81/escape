import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
import gpiozero
import board
import neopixel

from time import sleep

deviceId = "kampfhummel"

PRESSED = 0
UNPRESSED = 1

lightstrip = neopixel.NeoPixel(board.D18, 100, brightness = 1)
lightstrip.fill((255, 255, 255))

LED_PIN = 26  #GPIO26

light = gpiozero.LED(LED_PIN)
light.on()

GPIO.setmode(GPIO.BCM)
 

def power_on_animation():
    for i in range(len(lightstrip)):
        lightstrip[i] = (255, 255, 255)
        if GPIO.input(BUTTON_PIN) == 1:
            return
        sleep(0.02)

def power_off_animation(): 
    for i in range(len(lightstrip) - 1, -1, -1):
        lightstrip[i] = (0, 0, 0)
        if GPIO.input(BUTTON_PIN) == 0:
            return
        sleep(0.02)

UP = 1
DOWN = 0
lastState = UP

try:
    while True:
        
        i = 0
        
        sleep(0.2)
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
    GPIO.cleanup()
