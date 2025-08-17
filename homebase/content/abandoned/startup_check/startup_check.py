import paho.mqtt.client as mqtt
import os
import time
from time import sleep
import json


deviceId = "startup_check"

mq_ip = "192.168.5.11"

_jsonData = {
    "id": deviceId,
}

devices = {
    "abandoned_dock_keypad": "Keypad in der Schleuse",
    "abandoned_dock_door": "Card reader und Türe in der Schleuse",
    "abandoned_dock_comm_1": "Kommunikator (mit Screen) Schleuse",
    "dock_comm_1": "Kommunikations-Screen Schleuse",
    "abandoned_dock_comm_2": "Lichtsäule Schleuse",
    "fake_fingerprint": "Fake Fingerabdruck Leser bei Tür zu Crewraum",
    "abandoned_tech_power": "Hauptstrom (Taschenlampe) Rätsel",
    "abandoned_tech_circuit": "Stromverteilungsrätsel (Plättchen)",
    "abandoned_tech_pressure": "Druckmesser bei Recycler",
    "abandoned_tech_recycler": "Recycler",
    "recycler_screen": "Recycler Screen",
    "abandoned_tech_core": "AI Core",
    "abandoned_tech_music": "Background Musik",
    "abandoned_tech_comm_1": "Kommunikator (Screen, LEDs) Technik Raum",
    "abandoned_tech_comm_2": "LEDs über Recycler",
    "abandoned_tech_comm_3": "LEDs von oben nach unten im Technik Raum",
    "abandoned_crew_door": "Türe zum Crew Raum",
    "abandoned_crew_sound_fx": "Sound Effekte - Nachrichten (ohne Subwoofer)",
    "abandoned_crew_replicator": "Replikator (Subwoofer ist am gleichen Strom, braucht aber den Replikator nicht)",
    "abandoned_crew_overheat": "Kühlsystem",
    "abandoned_crew_exit": "Ausgangstür",
    "hans_olo": "Logbuch Hans Olo",
    "helen_rippli": "Logbuch Helen Rippli",
    "abandoned_crew_comm": "Kommunikator Crew Raum",
    "abandoned_cockpit_keypad": "Keypad im Cockpit",
    "abandoned_cockpit_floppy": "Datenträger RFID in Mittelkonsole Cockpit",
    "floppy_screen": "Bedienungs-Touchscreen in der Mittelkonsole",
    "console_screen": "Darstellungs-Screen in der Mittelkonsole",
    "abandoned_cockpit_orbital": "Orbital (leuchtende Ringe) im Cockpit",
    "abandoned_cockpit_joystick": "Joystickrätsel im Cockpit",
    "abandoned_cockpit_destruct": "Selbstzerstörungssystem im Cockpit",
}

missing_devices = devices.copy()

def show_missing():
    os.system('cls' if os.name == 'nt' else 'clear')
    print()
    print("Still missing (%s devices):" % len(missing_devices.keys()))
    for id, text in missing_devices.items():
        print("%s\t\t%s" % (id, text))

def sendUpdate():
    cpu_temp = "?"
    try:
        cpu_temp = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = cpu_temp[len("temp="):cpu_temp.index("'")]
    except Exception as e:
        print(e)

    jsonData = _jsonData
    jsonData["input"] = missing_devices
    show_missing()
    mqttc.publish("FromDevice/%s" % deviceId, json.dumps(jsonData))


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code):
    print(f"Connected with result code {reason_code}")
    jsonData = _jsonData
    jsonData["status"] = "Connected"

    for id, text in devices.items():
        client.subscribe("FromDevice/%s" % id)
    
    sendUpdate()

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global devices
    global missing_devices
    print(msg.topic)
    deviceId = msg.topic[len("FromDevice/"):]
    #print(msg.payload)
    #payload = json.loads(msg.payload.decode('utf-8'))
    if deviceId in devices.keys():
        try:
            missing_devices.pop(deviceId)
        except:
            # sometimes puzzles reconnect or send multiple messages.
            pass
        sendUpdate()

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

try:
    while True:
        sleep(0.2)
        if len(missing_devices.items()) == 0:
            break

        
       

except Exception as e:
    s = ('An exception occurred: {}'.format(e))
    sendUpdate()
    print(s)
    print("Cleaning up")