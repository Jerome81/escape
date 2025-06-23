import paho.mqtt.client as mqtt
import serial
from time import sleep


def connect_serial():

    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        ser.reset_input_buffer()
        return ser
    except Exception as e:
        s = ('An exception occurred: {}'.format(e))
        print(s)


_serial_connected = False

try:
    ser = None
    while True:

        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            line = line.strip()
            codeword = "Replikator: "
            if line.startswith(codeword):
                event = line[len(codeword)::]
                print(event)

        sleep(0.1)

except Exception as e:
    s = ('An exception occurred: {}'.format(e))
    print(s)
    print("Cleaning up")