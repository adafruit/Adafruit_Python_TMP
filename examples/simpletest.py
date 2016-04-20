#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Can enable debug output by uncommenting:
#import logging
#logging.basicConfig(level=logging.DEBUG)
import time

# Note that this will work with the TMP007 sensor too!  Just use the TMP006
# class below as-is.
import Adafruit_TMP.TMP006 as TMP006


# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0


# Default constructor will use the default I2C address (0x40) and pick a default I2C bus.
#
# For the Raspberry Pi this means you should hook up to the only exposed I2C bus
# from the main GPIO header and the library will figure out the bus number based
# on the Pi's revision.
#
# For the Beaglebone Black the library will assume bus 1 by default, which is
# exposed with SCL = P9_19 and SDA = P9_20.
#
# Remember this TMP006 code will work fine with the TMP007 sensor too!
sensor = TMP006.TMP006()

# Optionally you can override the address and/or bus number:
#sensor = TMP006.TMP006(address=0x42, busnum=2)

# Initialize communication with the sensor, using the default 16 samples per conversion.
# This is the best accuracy but a little slower at reacting to changes.
sensor.begin()

# Optionally initialize with a faster but less precise sample rate.  You can use
# any value from TMP006_CFG_1SAMPLE, TMP006_CFG_2SAMPLE, TMP006_CFG_4SAMPLE,
# TMP006_CFG_8SAMPLE, or TMP006_CFG_16SAMPLE for the sample rate.
#sensor.begin(samplerate=TMP006.CFG_1SAMPLE)

# Loop printing measurements every second.
print('Press Ctrl-C to quit.')
while True:
    obj_temp = sensor.readObjTempC()
    die_temp = sensor.readDieTempC()
    print('Object temperature: {0:0.3F}*C / {1:0.3F}*F'.format(obj_temp, c_to_f(obj_temp)))
    print('   Die temperature: {0:0.3F}*C / {1:0.3F}*F'.format(die_temp, c_to_f(die_temp)))
    time.sleep(1.0)
