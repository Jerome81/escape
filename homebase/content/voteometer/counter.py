import time
import board
import neopixel

LED = 30
pixels = neopixel.NeoPixel(board.D18, LED, brightness=1)

class Counter:

    total = 0
    total_votes = 0
    last_vote = 0
    is_button_light_on = False

    def vote(self, number):
        self.turn_button_light_off()
        self.last_vote = number * 20
        self.total = self.total + self.last_vote
        self.total_votes = self.total_votes + 1
    
    def average(self):
        if self.total_votes == 0:
            return 0
        else:
            return round(self.total / self.total_votes)
    
    def display_last_vote(self):
        for i in range(1, LED - 1):
            pixels[i - 1] = (0, 0, 0)
            pixels[i] = (255, 255, 0)
            time.sleep(LED/1000)
    
    def play_loaded_animation(self):
        for i in range(0, LED - 1):
            pixels[i] = (255, 255, 0)
            time.sleep(LED/1000)
        time.sleep(1)
        pixels.fill((0, 0, 0))
     

    def show_average(self):
        average = self.average()
        light = round(LED * (average / 100))
        print("Average is: %s" % average)
        pixels[light] = (0, 0, 255)
        time.sleep(2)
        pixels.fill((0, 0, 0))
    
    def turn_button_light_on(self):
        #TODO turn button lights on
        print("Turning button lights on")
        
    def turn_button_light_off(self):
        #TODO turn button lights off
        print("Turning button lights off")
