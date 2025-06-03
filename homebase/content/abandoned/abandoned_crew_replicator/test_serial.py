import paho.mqtt.client as mqtt
import serial
from time import sleep


deviceId = "abandoned_crew_replicator"

mq_ip = "192.168.178.11"


def connect_serial():
    global _serial_connected
    if _serial_connected:
        return
    
    try:
        ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        ser.reset_input_buffer()
        _serial_connected = True
        return ser
    except Exception as e:
        s = ('An exception occurred: {}'.format(e))
        print(s)


_serial_connected = False

try:
    ser = None
    while True:
        if _serial_connected == False:
            ser = connect_serial()
        
        if _serial_connected == False:
            sleep(5)
        else:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                print(line)

            sleep(0.1)

except Exception as e:
    s = ('An exception occurred: {}'.format(e))
    print(s)
    print("Cleaning up")