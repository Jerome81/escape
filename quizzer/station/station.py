from common import message_queue

class Station:

    def __init__(self):
        self.mq = message_queue.MessageQueue()
        self.mq.on_event(self.on_event)

    def on_event(self, message):
