import gpiozero
from time import sleep

button1 = gpiozero.Button(18, hold_time = 0.1, bounce_time = 0.2)
button2 = gpiozero.Button(23, hold_time = 0.1, bounce_time = 0.2)
button3 = gpiozero.Button(24, hold_time = 0.1, bounce_time = 0.2)

_cartridge_number = 0

def inserted(n):
    global _cartridge_number
    _cartridge_number = _cartridge_number + n
    print("Cartdridge number: %s" % _cartridge_number)

def removed(n):
    global _cartridge_number
    _cartridge_number = _cartridge_number - n
    print("Cartridge number: %s" % _cartridge_number)


button1.when_pressed = lambda: inserted(1)
button1.when_released = lambda: removed(1)

button2.when_pressed = lambda: inserted(2)
button2.when_released = lambda: removed(2)

button3.when_pressed = lambda: inserted(4)
button3.when_released = lambda: removed(4)


current = 0
print("Insert and remove cartridges")
while True:
    sleep(0.1)
    if current != _cartridge_number:
        if _cartridge_number == 0:
            print("Cartridge removed")
        else:
            print(_cartridge_number)