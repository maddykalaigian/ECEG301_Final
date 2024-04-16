import time
import board
import busio
import storage
import os
import digitalio
import adafruit_sdcard
import adafruit_adxl34x
import adafruit_character_lcd.character_lcd_i2c as character_lcd
from analogio import AnalogIn


"""
ACCELEROMETER
"""
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

"""
LCD SCREEN
"""

cols = 16
rows = 2
lcd = character_lcd.Character_LCD_I2C(i2c, cols, rows)
lcd.cursor = False

# to write to the screen
lcd.message = "Hello there \nHow are you?"
# to clear the screen
lcd.clear()


"""
SD CARD
"""
SD_CS = board.SD_CS  # setup for M0 Adalogger

# Connect to the card and mount the filesystem.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(SD_CS)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")


"""
# create/open a file and write a line of text
# "w" erases existing file and starts at the top
with open("/sd/test.txt", "w") as f:
    f.write("Hello world!\r\n")
    
# create/open a file and append ("a") text
with open("/sd/test.txt", "a") as f:
    f.write("This is another line!\r\n")

# open a file and read a line from it
with open("/sd/test.txt", "r") as f:
    print("Read line from file:")
    print(f.readline())

# read and print all lines from a file:
with open("/sd/test.txt", "r") as f:
    print("Printing lines in file:")
    line = f.readline()
    while line != '':
        print(line)
        line = f.readline()

# examples for our sensors
# just use the above loop to read all lines
# and change "test.txt" to desired text file  
    
print("Logging turbidity to sd card")
with open("/sd/turbidity.txt", "a") as f:
    f.write("turbidity data")
time.sleep(1)

print("Logging flow rate to filesystem")
with open("/sd/flow.txt", "a") as f:
    f.write("flow rate data")
time.sleep(1)

print("Logging accelerometer to filesystem")
with open("/sd/accelerometer.txt", "a") as f:
    f.write("accelerometer data")
time.sleep(1)

print("Logging GPS to filesystem")
with open("/sd/gps.txt", "a") as f:
    f.write("gps data")
time.sleep(1)

# edit while condition for accelerometer interrupt
# csv text file example (maybe better for NGO use?)
while True:
    # just random examples
    accelerometer_value = get_accelerometer_data()
    gps_timestamp = get_gps_timestamp()
    turbidity_value = get_turbidity_value()
    flow_rate_value = get_flow_rate_value()
    
    with open("/sd/sensor_data.csv", "a") as f:
        f.write(f"{accelerometer_value}, {gps_timestamp}, {turbidity_value}, {flow_rate_value}\n")
    print(f"Logged data to sensor_data.csv")
    time.sleep(1)

"""
