import time
import board
import busio
from analogio import AnalogIn
import adafruit_adxl34x
import adafruit_gps
import adafruit_character_lcd.character_lcd_i2c as character_lcd

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

while True:


    gps.update()

    if not gps.timestamp_utc:
        print("No time data from GPS yet")


    if not gps.has_fix:
        print("Waiting for fix...")
        continue

    print(
        "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
            gps.timestamp_utc.tm_mon,
            gps.timestamp_utc.tm_mday,
            gps.timestamp_utc.tm_year,
            gps.timestamp_utc.tm_hour,
            gps.timestamp_utc.tm_min,
            gps.timestamp_utc.tm_sec,
        )
    )
    print("Latitude: {0:.6f} degrees".format(gps.latitude))
    print("Longitude: {0:.6f} degrees".format(gps.longitude))


    print("Motion detected: %s" % accelerometer.events["motion"])
    time.sleep(1)
