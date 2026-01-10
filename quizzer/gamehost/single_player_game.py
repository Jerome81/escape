import sys
sys.path.append('../')

from common import message_queue
from time import sleep

import json

class SinglePlayerStation:
    def __init__(self):
        self.client_ready = False
        self.mq = message_queue.MessageQueue()
        self.mq.on_event(self.on_event)
        self.mq.on_connect(self.on_connect)

    def on_event(self, message):
        text = message.payload.decode('utf-8')
        print(text)

        if message.topic.startswith("FromStation/"):
            self.answer_received(message.topic.replace("FromStation/", ""), text.replace("Answer: ", ""))
        try:
            payload = json.loads(text)
        
            if payload["event"] is not None:
                event = payload["event"]
                if event == "Prepare game":
                    self.prepare_game(message)
                
                if event == "Start quiz":
                    self.start_quiz(message)
            
                return
        except Exception as e:
            # Text only message
            if text.startswith("Connected: "):
                self.on_station_connected(text.replace("Connected: ", ""))

    def on_connect(self, message, client):
        self.mq.register_for_room_topic()

    def send_question(self, question_nr):
        self.answers = []
        json_data = {
            "question": self.questions[question_nr]
        }
        print(json_data)
        self.mq.mqttc.publish("ToStation/1", json.dumps(json_data))
        print("sent")


    def answer_received(self, station, answer):
        print("Answer received from station '%s': %s" % (station, answer))
        self.answers = self.answers + [ { station: answer } ]

    def send_results(self):
        correct_answer = self.questions[self.current_question]["correctAnswer"]
        print("The correct answer was: %s" % correct_answer)
        for a in self.answers:
            for station, answer in a.items():
                json_data = {
                    "answer": correct_answer
                }
                if answer == correct_answer:
                    json_data["correct"] = 1
                    json_data["score"] = 100
                    self.mq.mqttc.publish("ToStation/1", json.dumps(json_data))
                else:
                    json_data["correct"] = 0
                    json_data["score"] = 0
                    self.mq.mqttc.publish("ToStation/1", json.dumps(json_data))
            
    def prepare_game(self, message):
        # Download quiz

        # Message each station with name
        pass

    def start_quiz(self, message):
        # Load local quiz
        self.load("quiz.json")
        self.current_question = 0

    def load(self, name):
        with open('quiz.json') as json_file:
            self.quiz = json.load(json_file)
        
    def on_station_connected(self, message):
        print("Client connected: " + message)
        if message in self.stations:
            print("Already registered: " + message)
        else:
            self.stations = self.stations + [message]
            print(self.stations)
            topic = "FromStation/%s" % message
            print("Subscribing to: %s" % topic)
            self.mq.mqttc.subscribe(topic)

    def wait_for_stations_to_register(self):
        while not len(self.stations) == 1:
            sleep(0.5)

    def wait_for_answers(self):
        while not len(self.answers) == 1:
            sleep(0.1)

    def start_game_loop(self):
        self.stations = []
        self.mq.connect()
        self.start_quiz("Test")
        self.wait_for_stations_to_register()
        self.quiz_meta_data = self.quiz[0]
        self.questions = self.quiz[1:]

        for question in self.questions:
            print(question)
            print("==========================")

        for i in range(0, 20):
            self.current_question = i
            self.send_question(i)
            self.wait_for_answers()
            self.send_results()
            sleep(5)

        sleep(5)
    
    def send_readyness(self):
        self.answers = []
        json_data = {
            "event": "get ready",
            "name": "Jerome"
        }
        print(json_data)
        self.mq.mqttc.publish("ToStation/1", json.dumps(json_data))
        print("sent")

    def test(self):
        self.stations = []
        self.mq.connect()
        self.send_readyness()

if __name__ == "__main__":
    sp = SinglePlayerStation()
    sp.test()
    #sp.start_game_loop()