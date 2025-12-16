import paho.mqtt.client as mqtt
from common import configuration
from time import sleep
import json

class MessageQueue:
    def __init__(self):
        self.config = configuration.get_config()
        self.mq_ip = self.config["mq_ip"]

    def connect(self):
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self._on_connect
        self.mqttc.on_message = self._on_message
        self.mqttc.username_pw_set(username="outpost", password="CallingHome")
        self.try_connect(self.mqttc)
        print("starting message queue.")
        self.mqttc.loop_start()

    def try_connect(self, client):
        disconnected = True
        while disconnected:
            try:   
                client.connect(self.mq_ip, 1883, 60)
                disconnected = False
            except Exception as e:
                print('An exception occured: {}'.format(e))
                sleep(5)

    ### Message Queue Events ###

    # The callback for when the client receives a CONNACK response from the server.
    def _on_connect(self, client, userdata, flags, reason_code):
        print(f"Connected with result code {reason_code}")
        
        if self.on_connect_method is not None:
            self.on_connect_method(self, client)
        #client.publish("ToGameHost", "%s is active" % self.config["station_id"])

    def on_connect(self, method):
        self.on_connect_method = method

    def on_event(self, method):
        self.on_event_method = method

    def register_for_room_topic(self):
        topic = "ToRoom/%s" % self.config["room_id"]
        print(topic)
        self.mqttc.subscribe(topic)

    def register_for_station_topic(self):
        topic = "ToStation/%s" % self.config["station_id"]
        print(topic)
        self.mqttc.subscribe(topic)


    # The callback for when a PUBLISH message is received from the server.
    def _on_message(self, client, userdata, msg):
        global _gameState
        print("%s: %s" % (msg.topic, msg.payload))
        if self.on_event_method is not None:
            self.on_event_method(msg)
