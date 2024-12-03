import RPi.GPIO as GPIO

import time
import board
import neopixel

LED = 47
BUTTON_LED = [4, 6, 12, 17]
BUTTON_LOCATION = [7, 18, 29, 40] # Up to how far should the light go when a button is pressed

pixels = neopixel.NeoPixel(board.D18, LED, brightness=0.5)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_LED[0], GPIO.OUT)
GPIO.setup(BUTTON_LED[1], GPIO.OUT)
GPIO.setup(BUTTON_LED[2], GPIO.OUT)
GPIO.setup(BUTTON_LED[3], GPIO.OUT)

class Counter:

    total = 0
    total_votes = 0
    last_vote = 0
    is_button_light_on = False

    def vote(self, number):
        print("Voting: %s" % number)
        self.last_vote = number
        self.total = self.total + ((number - 1) * 33)
        self.total_votes = self.total_votes + 1
    
    def average(self):
        if self.total_votes == 0:
            return 0
        else:
            return round(self.total / self.total_votes)
    
    def display_last_vote(self):
        for i in range(1, round(BUTTON_LOCATION[self.last_vote - 1])):
            pixels[i - 1] = (0, 0, 0)
            pixels[i] = (255, 255, 0)
            time.sleep(1 / LED)
    
    def play_loaded_animation(self):
        for i in range(0, len(BUTTON_LED)):
            self.turn_button_light_on(i)
       
        for i in range(0, LED - 1):
            pixels[i] = (255, 255, 0)
            time.sleep(1 / LED)
        time.sleep(1)
        pixels.fill((0, 0, 0))
        
        self.turn_button_lights_off()
     

    def show_average(self):
        average = self.average()
        light = round(LED * (average / 100))
        #print("Average is: %s" % average)
        pixels[light] = (0, 0, 255)
        time.sleep(2)
        pixels.fill((0, 0, 0))
    
    def turn_button_light_on(self, button):
        #print("Turning button lights on")
        GPIO.output(BUTTON_LED[button - 1], GPIO.HIGH)
        
    def turn_button_lights_on(self):
        for i in range(0, len(BUTTON_LED)):
            self.turn_button_light_on(i)
            time.sleep(0.15)

    def turn_button_light_off(self, button):
        #print("Turning button lights off")
        GPIO.output(BUTTON_LED[button - 1], GPIO.LOW)

    def turn_button_lights_off(self):
        for i in range(0, len(BUTTON_LED)):
            self.turn_button_light_off(i)
