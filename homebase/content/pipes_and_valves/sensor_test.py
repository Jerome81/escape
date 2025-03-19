
import smbus
import time
from time import sleep
import json

# Get I2C bus
bus = smbus.SMBus(1)
channels = [0x01, 0x02, 0x07]
sensor_address = 0x23
sensor_max_vals = [100]

def start_sensors(channels):
    for chan in channels:
        # BH1715 address, 0x23(35)
        # Send power on command
        #               0x01(01)        Power On
        channel(chan).write_byte(sensor_address, 0x01)

def channel(chan):
    bus.write_byte_data(0x70, 0x04, chan)  # 0x04 is for switching channels
    return bus

def read_sensors(channels, max_vals):
    for c in channels:
        # BH1715 address, 0x23(35)
        # Send continuous measurement command
        #               0x10(16)        Set Continuous high resolution mode, 1 lux resolution, Time = 120ms
        channel(c).write_byte(sensor_address, 0x10)

    time.sleep(0.2)

    vals = []
    i = 0
    for c in channels:
        # BH1715 address, 0x23(35)
        # Read data back, 2 bytes using General Calling
        # luminance MSB, luminance LSB
        data = channel(c).read_i2c_block_data (0x23, 2)

        # Convert the data
        luminance = (data[0] * 256 + data[1]) / 1.2
        vals.append(luminance)
        #vals.append(luminance * max_vals[i] / 1000)
        i = i + 1

    return vals

start_sensors(channels)

try:
    while True:
        print(read_sensors(channels, sensor_max_vals))
        sleep(0.2)


except Exception as e:
    print('An exception occurred: {}'.format(e))
    print("Cleaning up")
