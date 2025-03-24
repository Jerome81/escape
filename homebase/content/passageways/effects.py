import neopixel
from time import sleep
from random import randint
from datetime import datetime, timedelta

class Effects(object):

    def __init__(self, led_count, pin):
        self._lightstrip = neopixel.NeoPixel(pin, led_count, brightness = 1, auto_write=False)
        self._lightstrip.fill((255, 0, 0))
        self._lightstrip.show()
        self._led_count = led_count
        self._current_animation = "just light"
        self._step = -0.05
        self._brightness = 0.8
        self._last_animation = ""
        self._delayed_until = None



    ### Effects ###
    def start_pulse(self):  
        self._step = -0.05
        self._brightness = 0.8
        self._current_animation = "pulse"
        self.pulse()

    def pulse(self, speed = 0.05):
        self._lightstrip.brightness = self._brightness
        self._lightstrip.show()
        self._brightness = self._brightness + self._step
        if self._brightness < 0.2 or self._brightness > 0.8:
            self._step = -self._step

        sleep(speed)

    def wipe(self, color, transition_period = 2000, target_brightness = 1):
        steps = round(self._led_count / 2)
        diff_brightness = target_brightness - self._lightstrip.brightness
        bright_step = diff_brightness / steps
        for i in range(0, steps):
                self._lightstrip.brightness = self._lightstrip.brightness + bright_step
                self._lightstrip[i] = color
                self._lightstrip[(self._led_count - 1) - i] = color
                self._lightstrip.show()
                sleep((transition_period / 1000) / steps)

    def morph(self, start_color, destination_color, steps = 50, transition_period = 2000, target_brightness = 1):

        red_start = start_color[0]
        green_start = start_color[1]
        blue_start = start_color[2]
        
        diff_brightness = target_brightness - self._lightstrip.brightness
        bright_step = diff_brightness / steps
        
        red = start_color[0] - destination_color[0]
        green = start_color[1] - destination_color[1]
        blue = start_color[2] - destination_color[2]

        red_increment = red / steps
        green_increment = green / steps
        blue_increment = blue / steps

        for i in range(0, steps):
            new_red = round(red_start - (red_increment * i))
            new_green = round(green_start - (green_increment * i))
            new_blue = round(blue_start - (blue_increment * i))
            self._lightstrip.fill((new_red, new_green, new_blue))
            self._lightstrip.brightness = self._lightstrip.brightness + bright_step
            self._lightstrip.show()
            sleep((transition_period / 1000) / steps)

    def morph_to(self, destination_color):
        self.morph(self._lightstrip[0], (destination_color))

    def start_rain(self, rain_prob = 2, rain_color = ((0, 255, 0))):
        self._current_animation = "rain"
        self._rain_prob = rain_prob
        self._rain_color = rain_color
        for i in range(self._led_count):
            if randint(1, 10) <= self._rain_prob:
                self._lightstrip[i] = self._rain_color
            else:
                self._lightstrip[i] = ((0, 0, 0))
        self.rain()

    def rain(self):
        middle = round(self._led_count / 2)
        for i in range(1, middle):
            self._lightstrip[i - 1] = self._lightstrip[i]
        
        for i in range(self._led_count - 1, middle - 1, -1):
            self._lightstrip[i] = self._lightstrip[i - 1]
        
        if randint(1, 10) <= self._rain_prob:
            self._lightstrip[middle] = self._rain_color
        else:
            self._lightstrip[middle] = ((0, 0, 0))
            
        if randint(1, 10) <= self._rain_prob:
            self._lightstrip[middle - 1] = self._rain_color
        else:
            self._lightstrip[middle - 1] = ((0, 0, 0))
        self._lightstrip.show()


    def fill(self, color):
        self._lightstrip.fill(color)
        self._lightstrip.show()

    def just_light(self, color):
        self._current_animation = "just light"
        self._lightstrip.fill(color)
        self._lightstrip.show()

    def start_red_alert(self, color = ((255, 0, 0))):
        self.fill(color)
        self._current_animation = "red_alert"
        self.red_alert()

    def start_broken(self, color = ((255, 0, 0))):
        self.fill(color)
        self._current_animation = "broken"
        self.red_alert()


    def red_alert(self):
        if self._current_animation == "broken":
            # flicker about every 10th pulse
            if randint(1, 10) == 1:
                delays = [0.01, 0.01, 0.01, 1, 0.5, 0.1, 0.1, 0.5, 1, 0.01]
                for i in range(4, 4 + randint(1, 8)):
                    self._lightstrip.brightness = 0
                    self._lightstrip.show()
                    sleep(delays[randint(0, 9)])
                    self._lightstrip.brightness = 0.7
                    self._lightstrip.show()
        self.pulse(speed = 0.01)

    def start_enter(self, location):
        self._last_animation = self._current_animation
        self._current_animation = "enter"
        self._location = location

    def enter(self):

        if self._delayed_until == None:
            self._delayed_until = datetime.now() + timedelta(seconds= 2 * self._location)

        if datetime.now() > self._delayed_until:
            last_color = self._lightstrip[0]
            self._lightstrip.fill((255, 255, 255))
            self._lightstrip.brightness = .45
            self._lightstrip.show()
            sleep(5)
            self._current_animation = self._last_animation
            self._delayed_until = None
            self._last_animation = None
            self.morph_to(last_color)
        else:
            # Keep the last animation going until it's time to light on.
            self._current_animation = self._last_animation
            self.next_iteration()
            self._current_animation = "enter"

    def start_leave(self, location):
        self._last_animation = self._current_animation
        self._current_animation = "leave"
        self._location = location

    def leave(self):
        if self._delayed_until == None:
            self._delayed_until = datetime.now() + timedelta(seconds= 2 * (5 - self._location))

        if datetime.now() > self._delayed_until:
            last_color = self._lightstrip[0]
            self._lightstrip.fill((255, 255, 255))
            self._lightstrip.brightness = .45
            self._lightstrip.show()
            sleep(5)
            self._current_animation = self._last_animation
            self._delayed_until = None
            self._last_animation = None
            self.morph_to(last_color)
        else:
            # Keep the last animation going until it's time to light on.
            self._current_animation = self._last_animation
            self.next_iteration()
            self._current_animation = "leave"


    def next_iteration(self):
        if self._current_animation == "pulse":
            self.pulse()
        if self._current_animation == "enter":
            self.enter()
        if self._current_animation == "leave":
            self.leave()
        if self._current_animation == "rain":
            self.rain()
        if self._current_animation == "red_alert" or self._current_animation == "broken":
            self.red_alert()
        if self._current_animation == "just light":
            pass # no effect playing
