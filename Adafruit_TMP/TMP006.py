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
import logging
import math


# Coefficient values, found from this whitepaper:
# http://www.ti.com/lit/ug/sbou107/sbou107.pdf
TMP006_B0   = -0.0000294
TMP006_B1   = -0.00000057
TMP006_B2   = 0.00000000463
TMP006_C2   = 13.4
TMP006_TREF = 298.15
TMP006_A2   = -0.00001678
TMP006_A1   = 0.00175
TMP006_S0   = 6.4  # * 10^-14

# Default device I2C address.
TMP006_I2CADDR      = 0x40

# Register addresses.
TMP006_CONFIG       = 0x02
TMP006_MANID        = 0xFE
TMP006_DEVID        = 0xFF
TMP006_VOBJ         = 0x0
TMP006_TAMB         = 0x01

# Config register values.
TMP006_CFG_RESET    = 0x8000
TMP006_CFG_MODEON   = 0x7000
CFG_1SAMPLE         = 0x0000
CFG_2SAMPLE         = 0x0200
CFG_4SAMPLE         = 0x0400
CFG_8SAMPLE         = 0x0600
CFG_16SAMPLE        = 0x0800
TMP006_CFG_DRDYEN   = 0x0100
TMP006_CFG_DRDY     = 0x0080


class TMP006(object):
    """Class to represent an Adafruit TMP006 non-contact temperature measurement
    board.
    """

    def __init__(self, address=TMP006_I2CADDR, i2c=None, **kwargs):
        """Initialize TMP006 device on the specified I2C address and bus number.
        Address defaults to 0x40 and bus number defaults to the appropriate bus
        for the hardware.
        """
        self._logger = logging.getLogger('Adafruit_TMP.TMP006')
        if i2c is None:
            import Adafruit_GPIO.I2C as I2C
            i2c = I2C
        self._device = i2c.get_i2c_device(address, **kwargs)

    def begin(self, samplerate=CFG_16SAMPLE):
        """Start taking temperature measurements.  Samplerate can be one of
        TMP006_CFG_1SAMPLE, TMP006_CFG_2SAMPLE, TMP006_CFG_4SAMPLE,
        TMP006_CFG_8SAMPLE, or TMP006_CFG_16SAMPLE.  The default is 16 samples
        for the highest resolution.  Returns True if the device is intialized,
        False otherwise.
        """
        if samplerate not in (CFG_1SAMPLE, CFG_2SAMPLE, CFG_4SAMPLE, CFG_8SAMPLE,
            CFG_16SAMPLE):
            raise ValueError('Unexpected samplerate value! Must be one of: ' \
                'CFG_1SAMPLE, CFG_2SAMPLE, CFG_4SAMPLE, CFG_8SAMPLE, or CFG_16SAMPLE')
        self._logger.debug('Using samplerate value: {0:04X}'.format(samplerate))
        # Set configuration register to turn on chip, enable data ready output,
        # and start sampling at the specified rate.
        config = TMP006_CFG_MODEON | TMP006_CFG_DRDYEN | samplerate
        # Flip byte order of config value because write16 uses little endian but we
        # need big endian here.  This is an ugly hack for now, better to add support
        # in write16 for explicit endians.
        config = ((config & 0xFF) << 8) | (config >> 8)
        self._device.write16(TMP006_CONFIG, config)
        # Check manufacturer and device ID match expected values.
        mid = self._device.readU16BE(TMP006_MANID)
        did = self._device.readU16BE(TMP006_DEVID)
        self._logger.debug('Read manufacturer ID: {0:04X}'.format(mid))
        self._logger.debug('Read device ID: {0:04X}'.format(did))
        return mid == 0x5449 and did == 0x0067

    def sleep(self):
        """Put TMP006 into low power sleep mode.  No measurement data will be
        updated while in sleep mode.
        """
        control = self._device.readU16BE(TMP006_CONFIG)
        control &= ~(TMP006_CFG_MODEON)
        self._device.write16(TMP006_CONFIG, control)
        self._logger.debug('TMP006 entered sleep mode.')

    def wake(self):
        """Wake up TMP006 from low power sleep mode."""
        control = self._device.readU16BE(TMP006_CONFIG)
        control |= TMP006_CFG_MODEON
        self._device.write16(TMP006_CONFIG, control)
        self._logger.debug('TMP006 woke from sleep mode.')

    def readRawVoltage(self):
        """Read raw voltage from TMP006 sensor.  Meant to be used in the
        calculation of temperature values.
        """
        raw = self._device.readS16BE(TMP006_VOBJ)
        self._logger.debug('Raw voltage: 0x{0:04X} ({1:0.4F} uV)'.format(raw & 0xFFFF,
            raw * 156.25 / 1000.0))
        return raw

    def readRawDieTemperature(self):
        """Read raw die temperature from TMP006 sensor.  Meant to be used in the
        calculation of temperature values.
        """
        raw = self._device.readS16BE(TMP006_TAMB)
        self._logger.debug('Raw temperature: 0x{0:04X} ({1:0.4F} *C)'.format(raw & 0xFFFF,
            raw / 4.0 * 0.03125))
        return raw >> 2

    def readDieTempC(self):
        """Read sensor die temperature and return its value in degrees celsius."""
        Tdie = self.readRawDieTemperature()
        return Tdie * 0.03125

    def readObjTempC(self):
        """Read sensor object temperature (i.e. temperature of item in front of
        the sensor) and return its value in degrees celsius."""
        # Read raw values and scale them to required units.
        Tdie = self.readRawDieTemperature()
        Vobj = self.readRawVoltage()
        Vobj *= 156.25         # 156.25 nV per bit
        self._logger.debug('Vobj = {0:0.4} nV'.format(Vobj))
        Vobj /= 1000000000.0   # Convert nV to volts
        Tdie *= 0.03125        # Convert to celsius
        Tdie += 273.14         # Convert to kelvin
        self._logger.debug('Tdie = {0:0.4} K'.format(Tdie))
        # Compute object temperature following equations from:
        # http://www.ti.com/lit/ug/sbou107/sbou107.pdf
        Tdie_ref = Tdie - TMP006_TREF
        S = 1.0 + TMP006_A1*Tdie_ref + TMP006_A2*math.pow(Tdie_ref, 2.0)
        S *= TMP006_S0
        S /= 10000000.0
        S /= 10000000.0
        Vos = TMP006_B0 + TMP006_B1*Tdie_ref + TMP006_B2*math.pow(Tdie_ref, 2.0)
        fVobj = (Vobj - Vos) + TMP006_C2*math.pow((Vobj - Vos), 2.0)
        Tobj = math.sqrt(math.sqrt(math.pow(Tdie, 4.0) + (fVobj/S)))
        return Tobj - 273.15
