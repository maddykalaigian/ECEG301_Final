import time
import board
import busio
from analogio import AnalogIn
import adafruit_adxl34x
import adafruit_gps
import adafruit_sdcard
import storage
import digitalio

import adafruit_character_lcd.character_lcd_i2c as character_lcd
from digitalio import DigitalInOut, Direction, Pull

def get_voltage(pin):
    return (pin.value * 3.3) / 65536

def volt_to_NTU(v):
    pass

i2c = board.I2C()  # uses board.SCL and board.SDA
uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# Turbidity
analog_in = AnalogIn(board.A1)

# For ADXL343
accelerometer = adafruit_adxl34x.ADXL343(i2c)
# For ADXL345
# accelerometer = adafruit_adxl34x.ADXL345(i2c)

accelerometer.enable_motion_detection()
# alternatively you can specify the threshold when you enable motion detection for more control:
# accelerometer.enable_motion_detection(threshold=10)

gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps.send_command(b"PMTK220,1000")

#For LCD Screen
#THIS DOES NOT WORK YET, IT IS A WORK IN PROGRESS
cols = 16
rows = 2
lcd = character_lcd.Character_LCD_I2C(i2c,cols,rows)
lcd.backlight = True
lcd.message = "Hello World"

flow = DigitalInOut(board.D5)
flow.direction = Direction.INPUT
flow.pull = Pull.DOWN

flowNow = flow.value
flowPrev = flow.value
edgeCounter = 0

timeNow = time.monotonic()
timePrev = timeNow


spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D10)

sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)

storage.mount(vfs, "/sd")



while True:
    # gps.update()

#     if not gps.timestamp_utc:
#         print("No time data from GPS yet")


#     if not gps.has_fix:
#         print("Waiting for fix...")
#         continue

#     print("{}/{}/{} {:02}:{:02}:{:02}".format(
#             gps.timestamp_utc.tm_mon,
#             gps.timestamp_utc.tm_mday,
#             gps.timestamp_utc.tm_year,
#             gps.timestamp_utc.tm_hour,
#             gps.timestamp_utc.tm_min,
#             gps.timestamp_utc.tm_sec,
#         ))

#     time_gps = "{}/{}/{} {:02}:{:02}:{:02}".format(
#             gps.timestamp_utc.tm_mon,
#             gps.timestamp_utc.tm_mday,
#             gps.timestamp_utc.tm_year,
#             gps.timestamp_utc.tm_hour,
#             gps.timestamp_utc.tm_min,
#             gps.timestamp_utc.tm_sec,
#         )

#     print(time_gps)

#     latitude = "{0:.6f}".format(gps.latitude)
#     longitude = "{0:.6f}".format(gps.longitude)

#     with open("/sd/test.csv", "a") as f:
#         f.write(time_gps+","+latitude+","+longitude+"\r\n")

#     print("done!")
#     time.sleep(5)


#     with open("/sd/test.csv", "r") as f:
#         print("Read line from file:")
#         print(f.readline())

    timeNow = time.monotonic()
    flowNow = flow.value

    if(flowNow != flowPrev and flowNow):
        edgeCounter += 1

    if((timeNow - timePrev) > 1.0):
        print("Flow rate (pulses):"+ str(edgeCounter))
        print("Motion detected: %s" % accelerometer.events["motion"])
        print(str(get_voltage(analog_in)) + " V")
        edgeCounter = 0
        timePrev = timeNow

    flowPrev = flowNow


