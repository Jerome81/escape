from time import sleep
import json
import paho.mqtt.client as mqtt
import gpiozero
import RPi.GPIO as GPIO
import os


mq_ip = "192.168.5.11"
deviceId = "abandoned_tech_recycler"

_gameState = "STOPPED"
_puzzleState = "INACTIVE"
_currentData = [0, 0, 0]
_solution = [1, 1, 1]
_stones_set_correctly = False
_pressure_correct = False

BUTTON_PIN = 18  #GPIO18

button1 = gpiozero.Button(BUTTON_PIN, hold_time = 1, bounce_time = 0.2)
button2 = gpiozero.Button(23, hold_time = 1, bounce_time = 0.2)
button3 = gpiozero.Button(24, hold_time = 1, bounce_time = 0.2)

# initialize trap door
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

# initialize cartridge door
GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.OUT)

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}

def on_unstoned(stone):
    global _currentData
    print("Unstoned %s" % stone)
    _currentData[stone] = 0
    sendUpdate()

def on_stoned(stone):
    global _currentData
    print("Stoned %s" % stone)
    _currentData[stone] = 1
    sendUpdate()

def lock_trapdoor():
    GPIO.setup(12, GPIO.LOW)
    print("Trapdoor locked")

def unlock_trapdoor():
    GPIO.setup(12, GPIO.HIGH)
    print("Trapdoor unlocked")

def lock_cartridgedoor():
    GPIO.setup(16, GPIO.LOW)
    print("Cartridge door locked")

def unlock_cartridgedoor():
    GPIO.setup(16, GPIO.HIGH)
    print("Cartridge door unlocked")

button1.when_pressed = lambda: on_unstoned(0)
button1.when_released = lambda: on_stoned(0)

# button2 is different
button2.when_pressed = lambda: on_stoned(1)
button2.when_released = lambda: on_unstoned(1)

button3.when_pressed = lambda: on_unstoned(2)
button3.when_released = lambda: on_stoned(2)


### Game events ###
def on_event(event):
    global _pressure_correct
    if event == "Pressure correct":
        _pressure_correct = True
    
    if event == "Pressure incorrect":
        _pressure_correct = False   

    if event == "All devices powered":
        on_activate()

    if event == "Produce cartridge":
        on_solved(mqttc)


### Global commands ###
def on_started():
    pass

def on_stopped():
    pass

def on_language_change(language):
    print("Nothing required for language change to %s." % language)

def sendUpdate():
    print("Game is: %s - Puzzle is: %s" % (_gameState, _puzzleState))

    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except e:
        print(e)

    jsonData = _jsonData
    jsonData["input"] = (_currentData)
    jsonData["state"] = _puzzleState
    jsonData["game_state"] = ("%s - %s" % (_gameState, cpu_temp))
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))


def stones_set_correctly(client):
    global _stones_set_correctly
    if _stones_set_correctly == True:
        return  # Message was already sent
    
    _stones_set_correctly = True
    jsonData = {
        "event": "Stones set correctly"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))


def stones_set_incorrectly(client):
    global _stones_set_correctly
    if _stones_set_correctly == False:
        return  # Message was already sent

    _stones_set_correctly = False
    jsonData = {
        "event": "Stones missing"
    }
    client.publish("ToDevice/All", json.dumps(jsonData))

def play_sound(file):
    os.system("mpg321 %s" % file)
    

### Puzzle commands ###
def on_solved(client):
    global _puzzleState
    play_sound("Analyse_3.mp3 &")
    sleep(1)
    unlock_trapdoor()
    _puzzleState = "SOLVED"
    sendUpdate()
    jsonData = {
        "event": "Cartridge produced"
    }
    client.publish("ToDevice/All", json.dumps(jsonData)) 
    sleep(2)
    play_sound("recycler_working.mp3")
    unlock_cartridgedoor()


def on_reset():
    global _puzzleState
    _puzzleState = "INACTIVE"
    lock_trapdoor()
    lock_cartridgedoor()
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
        if 'event' in payload:
            on_event(payload["event"])
        if 'language' in payload:
            on_language_change(payload["language"])
            

    if msg.topic == "ToDevice/%s" % deviceId:
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
    while disconnected:
        try:   
            client.connect(mq_ip, 1883, 60)
            disconnected = False
        except Exception as e:
            print('An exception occured: {}'.format(e))
            sleep(5)

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")

connect(mqttc)

print("starting message queue.")
mqttc.loop_start()

lock_trapdoor()
lock_cartridgedoor()

try:
    while(True):
        if _gameState == "STARTED":
            if _puzzleState == "ACTIVE":
                if _currentData == _solution:
                    stones_set_correctly(mqttc)
                else:
                    stones_set_incorrectly(mqttc)
                
        sleep(0.1)

except Exception as e:
    print('An exception occurred: {}'.format(e))
finally:
    GPIO.cleanup
        
   