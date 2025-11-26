import os
import paho.mqtt.client as mqtt
import json
import gpiozero
import neopixel
import board
from time import sleep
from random import randint
from random import shuffle

_solution_joystick = ["E", "W", "S", "N", "W"]  # MUST BE THE SAME AS IN JOYSTICK
_correct_inputs = 0

l = neopixel.NeoPixel(board.D18, 109, brightness = 0.8, auto_write = False)
l.fill((0, 0, 255))
l.show()

button_pressed = False
total_tries = 0
_easy_ending = True

mq_ip = "192.168.5.11"
deviceId = "abandoned_cockpit_orbital"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"

_jsonData = {
    "id": deviceId,
    "description": "Reagieren müssen sie.",
}

level_start = [0, 60, 92]
level_leds = [60, 32, 12]
level_speed = [0.005, 0.01, 0.02]
level_min_speed = [0.02, 0.03, 0.06]

l.fill((0, 0, 0))

BUTTON_PIN = 14  #GPIO14
button = gpiozero.Button(BUTTON_PIN, hold_time = 0.02, bounce_time = 0.1)

LED_PIN = 26  #GPIO26
light = gpiozero.LED(LED_PIN)
light.on()

def on_click():
    global button_pressed
    global total_tries
    total_tries = total_tries + 1
    print("button pressed %s" % total_tries)
    button_pressed = True
    light.on()

def diff_pixel(current_pixel, level, direction, amount):
    pixel = current_pixel + amount * (-direction)
    if pixel > level_start[level] + level_leds[level] - 1:
        return pixel - level_leds[level]
    if pixel < level_start[level]:
        return level_leds[level] + pixel
    return pixel

def light_up(pixels, goal_led):
    for color in [(255, 0, 0), (255, 51, 51), (204, 0, 0), (102, 0, 0), (20, 0, 0)]:
        for i in pixels:
            l[i] = color
        l.show()
        sleep(0.04)
    l.fill((0, 0, 0))
    l[goal_led] = (255, 255, 0)
    l.show()

def level_solved(level):
    for i in range(level_start[level], level_start[level] + level_leds[level]):
        l[i] = ((255, 255, 0))
    l.show()
    colors = [(255, 255, 102), (204, 204, 0), (102, 102, 0), (20, 20, 0), (0, 0, 0) ]
    for color in colors:
        leds = list(range(level_start[level], level_start[level] + level_leds[level]))
        shuffle(leds)
        while(len(leds) > 0):
            l[leds.pop(0)] = color
            l.show()
            sleep(0.005 * (level + 1))

def go_around(level, color, direction):
    global button_pressed
    nextPixel = level_start[level]
    solved = False
    goal_led = randint(level_start[level], level_start[level] + level_leds[level] - 1)
    l[goal_led] = ((255, 255, 0))
    after = []
    before = []
    for i in range(1, round(level_leds[level] / 2)):
        after.append(diff_pixel(goal_led, level, direction, i))
        before.append(diff_pixel(goal_led, level, -direction, i))

    speed = level_speed[level]
    while(True):
        lastPixel = nextPixel
        if button_pressed:
            l[lastPixel] = ((255, 255, 0))
            #print("Last: %s / Goal: %s" % (nextPixel, goal_led))
            #sleep(0.2)
            speed = speed + level_speed[level]
            if speed > level_min_speed[level]:
                speed = level_min_speed[level]
            button_pressed = False
            light.off()
            if nextPixel == goal_led:
                level_solved(level)
                return
            else:
                if nextPixel in after:
                        light_up(after, goal_led)
                else:
                        light_up(before, goal_led)

        nextPixel = nextPixel + direction
        if nextPixel > level_start[level] + level_leds[level] - 1:
                nextPixel = level_start[level]
        if nextPixel < level_start[level]:
                nextPixel = level_start[level] + level_leds[level] - 1
        l[lastPixel] = (51, 153, 255)
        if nextPixel == goal_led:
            l[nextPixel] = (0, 0, 0)
        else:
            l[nextPixel] = (255, 255, 0) 
        l[diff_pixel(nextPixel, level, direction, 2)] = (51, 102, 204)
        l[diff_pixel(nextPixel, level, direction, 3)] = (0, 51, 102)
        l[diff_pixel(nextPixel, level, direction, 4)] = (0, 10, 20)
        blank = diff_pixel(nextPixel, level, direction, 5)
        if blank == goal_led:
            l[blank] = (255, 255, 0)
        else:
            l[blank] = (0, 0, 0)

        l.show()

        sleep(speed)

def show_solution():
        l[108] = ((0, 255, 0))
        l.show()
        sleep(0.8)
        l[107] = ((0, 0, 255))
        l.show()        
        sleep(0.8)
        l[106] =  ((255, 0, 0))
        l.show()
        sleep(0.8)
        l[105] = ((255, 255, 0))
        l.show()
        sleep(0.8)
        l[104] = ((0, 0, 255))
        l.show()
        sleep(0.8)
        

### MQ send ###

def sendUpdate():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except Exception as e:
        print(e)

    jsonData = _jsonData
    jsonData["input"] = level
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = ("%s - %s" % (_gameState, cpu_temp))
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))
    

def attract():
    if _puzzleState == "SOLVED":
        l.fill((0, 0, 0))
        l.show()
        show_solution()
    else:
        for i in range(5):
            l.fill((0, 0, 255))
            l.show()
            sleep(0.3)
            l.fill((0, 0, 0))
            l.show()

### Game events ###
def on_event(event):
    global _easy_ending
    if event == "Activate orbital":
        on_activate()

    if event == "Easy ending":
        _easy_ending = True
    
    if event == "Hard ending":
        _easy_ending = False

    if event == "Power down":
        on_reset()
    
    if event == "Attract":
        attract()
    
def on_try_solve(input):
    global _correct_inputs
    if input == _solution_joystick[_correct_inputs]:
        l[108 - _correct_inputs] = (0, 0, 0)
        l.show()
        _correct_inputs = _correct_inputs + 1
        print("Correct inputs: %s" % _correct_inputs)

    else:
        _correct_inputs = 0
        l[104] = (0, 0, 0)
        l[105] = (0, 0, 0)
        l[106] = (0, 0, 0)
        l[107] = (0, 0, 0)
        l[108] = (0, 0, 0)
        l.show()
        sleep(0.5)
        show_solution()

### Global commands ###
def on_started():
    l.fill((0, 0, 0))
    l.show()
    sendUpdate()
    pass

def on_stopped():
    l.fill((0, 0, 255))
    l.show()
    sendUpdate()
    pass

def on_language_change(language):
    print("Nothing required for language change to %s." % language)
    

### Puzzle commands ###
def on_solved(client):
    global _puzzleState
    global level
    _puzzleState = "SOLVED"
    level = 3
    show_solution()
    sendUpdate()
    if _easy_ending:
        jsonData = {
            "event": "Communication channel established"
        }
        client.publish("ToDevice/All", json.dumps(jsonData))
    else:    
        jsonData = {
            "event": "Access granted"
        }
        client.publish("ToDevice/All", json.dumps(jsonData))
    client.publish("Stats", json.dumps( {"Orbital": total_tries } ))

def on_reset():
    global _puzzleState
    global level
    global total_tries
    _puzzleState = "INACTIVE"
    l[104] = (0, 0, 0)
    l[105] = (0, 0, 0)
    l[106] = (0, 0, 0)
    l[107] = (0, 0, 0)
    l[108] = (0, 0, 0)
    l.show()
    level = 0
    total_tries = 0
    sendUpdate()

def on_activate():
    global _puzzleState
    _puzzleState = "ACTIVE"
    sendUpdate()


### Message Queue Events ###

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    jsonData = _jsonData
    jsonData["status"] = "Connected"

    client.subscribe("ToDevice/%s" % deviceId)
    client.subscribe("ToDevice/All")
    client.publish("ToHost", json.dumps(jsonData))
    client.publish("FromDevice/%s" % deviceId, json.dumps(_jsonData))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global _gameState
    print(msg.topic)
    print(msg.payload)
    payload = json.loads(msg.payload.decode('utf-8'))

    if msg.topic == "ToDevice/All":
        if 'gameState' in payload:
            _gameState = payload["gameState"]
            if _gameState == "STARTED":
                on_started()
            if _gameState == "STOPPED":
                on_stopped()
            if _gameState == "RESET":
                on_reset()
        if 'language' in payload:
            on_language_change(payload["language"])

    if 'event' in payload:
        on_event(payload["event"])

    if msg.topic == "ToDevice/%s" % deviceId:
        
        if 'try_solve' in payload:
            on_try_solve(payload["try_solve"])

        if 'command' in payload:
            command = payload["command"]
            if command == "SOLVED":
                on_solved(client)
            if command == "RESET":
                on_reset()
            if command == "ACTIVATE":
                on_activate()

def connect(client):
    disconnected = True
    i = 0
    while disconnected:
        try:   
            client.connect(mq_ip, 1883, 60)
            disconnected = False
        except Exception as e:
            l[i] = (255, 0, 0)
            l.show()
            i = i + 1
            if i >= len(l):
                l.fill((200, 0, 0))
                l.show()
                i = 0
            print('An exception occured: {}'.format(e))
            sleep(5)

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

connect(mqttc)

print("starting message queue.")
mqttc.loop_start()

button.when_pressed = lambda: on_click()

level = 0
light.off()
sendUpdate()

try:
    while True:
        
        if _gameState == "STOPPED":
            continue

        if _puzzleState == "ACTIVE":
            go_around(level, ((0, 0, 255)), 1)
            level = level + 1
            sendUpdate()
            if level == 3:
                on_solved(mqttc)

        sleep(0.2)

        
except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
