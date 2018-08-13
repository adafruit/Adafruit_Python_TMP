
DEPRECATED LIBRARY Adafruit Python TMP006
===================

This library has been deprecated!

the tmp006 and tmp007 are no longer made, and we are now only using our circuitpython sensor libraries in python

we are leaving the code up for historical/research purposes but archiving the repository.

if you happen to have one, check out this guide for using the tmp007 with python!
https://learn.adafruit.com/adafruit-tmp007-sensor-breakout

#

Python library for accessing the TMP006 & TMP007 non-contact temperature sensor on a Raspberry Pi or Beaglebone Black.

Designed specifically to work with the Adafruit TMP006 sensor ----> https://www.adafruit.com/products/1296

To install, first make sure some dependencies are available by running the following commands (on a Raspbian
or Beaglebone Black Debian install):

````
sudo apt-get update
sudo apt-get install build-essential python-dev python-smbus
````

Then download the library by clicking the download zip link to the right and unzip the archive somewhere on your Raspberry Pi or Beaglebone Black.  Then execute the following command in the directory of the library:

````
sudo python setup.py install
````

Make sure you have internet access on the device so it can download the required dependencies.

See examples of usage in the examples folder.  Note that the example code and classes
use the TMP006 name but will work fine with a TMP007 sensor too.

Adafruit invests time and resources providing this open source code, please support Adafruit and open-source hardware by purchasing products from Adafruit!

Written by Tony DiCola for Adafruit Industries.
MIT license, all text above must be included in any redistribution
