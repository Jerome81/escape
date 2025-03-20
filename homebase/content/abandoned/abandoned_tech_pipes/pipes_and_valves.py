
import paho.mqtt.client as mqtt
import json

from random import randint
from time import sleep

deviceId = "PipesAndValves"

_gameState = "STOPPED"
_puzzleState = "UNSOLVED"
_solution = ["12", "44", "88", "17"]
_currentVals = ["00", "00", "00", "00"]

_jsonData = {
    "id": deviceId,
    "description": ("Lösung: %s" % _solution),
}


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    jsonData = _jsonData
    jsonData["status"] = "Connected"

    client.subscribe("ToDevice/%s" % deviceId)
    client.subscribe("ToDevice/All")
    client.publish("ToHost", json.dumps(jsonData))
    client.publish("FromDevice/%s" % deviceId, json.dumps(_jsonData))

def sendPuzzleState():
    jsonData = _jsonData
    jsonData["state"] = _puzzleState
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))

def puzzle_solved():
    global _puzzleState
    _puzzleState = "SOLVED"
    sendPuzzleState()
    print("Door unlocked")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global _gameState
    print(msg.topic)
    print(dir(msg))
    print(userdata)
    print(msg.payload)
    payload = json.loads(msg.payload.decode('utf-8'))
    print(payload)

    if msg.topic == "ToDevice/All":
        if 'gameState' in payload:
            _gameState = payload["gameState"]


    if msg.topic == "ToDevice/%s" % deviceId:
        global _puzzleState
        if 'command' in payload:
            command = payload["command"]
            if command == "SOLVED":
                puzzle_solved()
            if command == "RESET":
                _puzzleState = "UNSOLVED"
                sendPuzzleState()


def sendUpdate():
    jsonData = _jsonData
    
    jsonData["input0"] = _currentVals[0]
    jsonData["input1"] = _currentVals[1]
    jsonData["input2"] = _currentVals[2]
    jsonData["input3"] = _currentVals[3]
    
    jsonData["state"] = _puzzleState
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))
    if guess == "1234":
        puzzle_solved()
    
    

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username="outpost", password="CallingHome")
mqttc.connect("192.168.178.11", 1883, 60)

print("starting message queue.")
mqttc.loop_start()


while True:
    sleep(1)
    print(_gameState)
    if _gameState == "STARTED":
        guess = ""
        if _puzzleState == "SOLVED":
            break
        guess = guess + ("%02d" % randint(0, 99))
        _currentVals[randint(0, 3)] = guess
        print(_currentVals)
        sendUpdate()
        sleep(2)

   
    