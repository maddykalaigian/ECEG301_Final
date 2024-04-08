# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
from analogio import AnalogIn
import adafruit_adxl34x

def get_voltage(pin):
    return (pin.value * 3.3) / 65536
    
def volt_to_NTU(v):
    return -1120.4*v**2 + 5742.3*v - 4352.9

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# Turidity
analog_in = AnalogIn(board.A1)

# For ADXL343
accelerometer = adafruit_adxl34x.ADXL343(i2c)
# For ADXL345
# accelerometer = adafruit_adxl34x.ADXL345(i2c)

accelerometer.enable_motion_detection()
# alternatively you can specify the threshold when you enable motion detection for more control:
# accelerometer.enable_motion_detection(threshold=10)

while True:
    print("Motion detected: %s" % accelerometer.events["motion"])
    print(str(get_voltage(analog_in)) + " V")
    time.sleep(0.5)
