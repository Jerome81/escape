import board
import neopixel
from time import sleep

LEDS = 48
light = neopixel.NeoPixel(board.D18, LEDS, brightness = 1, auto_write = False)

color = (255, 0, 0)
for i in range(0, 48):
    if i > 6 and i < 19:
        color = (0, 0, 255)
    if i > 18 and i < 31:
        color = (255, 255, 0)
    if i > 30 and i < 43:
        color = (0, 255, 0)
    if i > 42:
        color = (255, 0, 0)
    light[i] = color
    light.show()
    sleep(0.05)
