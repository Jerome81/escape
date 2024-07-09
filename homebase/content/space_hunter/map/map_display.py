from flask import Flask, render_template, send_from_directory
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit, disconnect
import time
import subprocess


map_display = Flask(__name__)

cors = CORS(map_display)
map_display.config['CORS_HEADERS'] = 'Content-Type'

socket_ = SocketIO(map_display, async_mode=None)

@map_display.route('/map')
def main():
    return render_template('map.html')

@map_display.route('/<path:path>')
def send_report(path):
    return send_from_directory('', path)

@map_display.get("/force_refresh")
def force_refresh():
    print(trigger_refresh)
    trigger_refresh = True
    return "OK"

@socket_.on('needs_refresh', namespace='/refresh')
def refresh(data):
    while True:
        try:
            trigger_refresh = True
            if trigger_refresh:
                emit('refresh', {'result': "result"})
                trigger_refresh = False
            
            
               
        except Exception as ex:
            print(ex)

        time.sleep(1) 


if __name__ == '__main__':
    trigger_refresh = True
    socket_.run(map_display, host='0.0.0.0', port=80, debug=True)