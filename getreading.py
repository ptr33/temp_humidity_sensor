#!/usr/bin/env python3

import json
import paho.mqtt.publish as publish
import subprocess
import re
import sys
import time


DHT_PROGRAM = './Adafruit_DHT_Driver/Adafruit_DHT'
SUDO_PROGRAM = '/usr/bin/sudo'
# median of the measurements is calculated; use odd number only
NUMBER_OF_MEASUREMENTS = 5
MAX_RETRIES = 5


def get_sensor_data(device, gpio_pin):
    # Run the DHT program to get the humidity and temperature readings!
    # need to run as root

    output = subprocess.check_output([SUDO_PROGRAM, DHT_PROGRAM, device, gpio_pin]
                                    ).decode(sys.stdout.encoding)
    print(output)
    matches = re.search(r'Temp =\s+([0-9.]+)', output)
    if (not matches):
        return None
    temp = float(matches.group(1))

    # search for humidity printout
    matches = re.search(r'Hum =\s+([0-9.]+)', output)
    if (not matches):
        return None
    humidity = float(matches.group(1))

    # print(f"Temperature: {temp} C")
    # print(f"Humidity:    {humidity} %")

    return temp, humidity


def calc_dewpoint(temp, humidity):
    '''Approximate Dewpoint'''
    return temp-(100-humidity)/5


# Open and read the JSON file
with open('config.json', 'r') as file:
    config = json.load(file)

temp_array = []
humidity_array = []
i = 0
retries = 0
while i < NUMBER_OF_MEASUREMENTS:
    if i>0: # check if this is not the first measurement
        time.sleep(3)  # wait time between measurements
    ret = get_sensor_data(config['hardware_device'], config['hardware_gpio_pin'])
    if ret is not None:
        temp, humidity = ret
        temp_array.append(temp)
        humidity_array.append(humidity)
        i = i + 1
    else:
        if retries >= MAX_RETRIES:
            print(f'Access to sensor failed even with {retries} retries')
            sys.exit(1)
        else:
            retries = retries + 1

# now get median of list
temp = sorted(temp_array)[NUMBER_OF_MEASUREMENTS // 2]
humidity = sorted(humidity_array)[NUMBER_OF_MEASUREMENTS // 2]
dewpoint = calc_dewpoint(temp, humidity)
# round to 1/10's degrees
dewpoint = int(dewpoint*10)/10


print(f'Selected {temp} C and {humidity} % dewpoint {dewpoint} C')

# output to mqtt server
# publish.single(config['topic_temperature'], 25.3, **config['server'])
msgs  = [[config['topic_temperature'], temp],
         [config['topic_humidity'], humidity],
         [config['topic_dewpoint'], dewpoint]]
#         [config['topic_dewpoint'], f'{dewpoint}:0.1f']]
publish.multiple(msgs, **config['server'])

# above command throws an exception if not successful
print(f'Sucessfully published to MQTT client', config['server']['hostname'])
