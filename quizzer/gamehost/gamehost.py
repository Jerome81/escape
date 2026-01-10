import sys
sys.path.append('../')

from common import message_queue

class Gamehost:

    def __init__(self):
        self.mq = message_queue.MessageQueue()
        self.mq.on_event(self.on_event)
        self.mq.on_connect(self.on_connect)

    def on_event(self, message):
        print(message)
        if message["event"] is not None:
            event = message["event"]
            if event == "Prepare game":
                self.prepare_game(message)
            
            if event == "Start quiz":
                self.start_quiz(message)
        
            return
        
        if message.startswith("Conntected: "):
            self.on_station_connected(message.replace("Connected: ", ""))

    def on_connect(self, message):
        self.mq.register_for_room_topic()

    def prepare_game(self, message):
        pass

    def start_quiz(self, message):
        pass

    def on_station_connected(self, message):
        pass