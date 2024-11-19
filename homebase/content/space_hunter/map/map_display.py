import sys
sys.path.append('../')

import threading
import socket

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit, disconnect

from general.register import send_status


import time
import subprocess

map_display = Flask(__name__)

cors = CORS(map_display)
map_display.config['CORS_HEADERS'] = 'Content-Type'

socket_ = SocketIO(map_display, async_mode=None)
cache = {}

send_status("map", "Ready")

@map_display.route('/map')
def main():
    return render_template('map.html')

@map_display.route('/<path:path>')
def send_report(path):
    return send_from_directory('', path)

@map_display.get("/jump_complete/<direction>/<newX>/<newY>")
def jump_complete(direction, newX, newY):
    print("Triggering refresh on ", threading.currentThread())
    cache["event"] = ["jump_complete", [direction, newX, newY]]
    return "OK"

@socket_.on('needs_refresh', namespace='/refresh')
def refresh(data):
    while True:
        try:
            print(".", end = " ")
            if "event" in cache:
                print("Checking refresh on ", threading.currentThread(), " - ", cache["event"])
                print("Refreshing")
                emit('refresh', {'event': cache["event"][0], 'data': cache["event"][1]})
                del cache["event"]
            
            
               
        except Exception as ex:
            print(ex)

        time.sleep(0.1) 


if __name__ == '__main__':
    socket_.run(map_display, host='0.0.0.0', port=80, debug=True)