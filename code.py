import time
import math
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

'''
TODO:


'''


'''
 -------------------- Helper Functions --------------------
'''

def get_voltage(pin):
    return (pin.value * 3.3) / 65536

def volt_to_NTU(v):
    return 8.07*math.exp(0.671*v)

def pulse_to_volume(p, delay):  # takes in pulses and measuring period and returns L/min
    return p*2.3/1000*60/delay

'''
-------------------- Initial Setup --------------------
'''

# Initialize serial ports
i2c = board.I2C()       # LCD and accelerometer
uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)    # GPS
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)        # SD card
cs = digitalio.DigitalInOut(board.D10)

# Turbidity sensor
turbidityPin = AnalogIn(board.A1)
# Turbidity vars
turbidityVal = volt_to_NTU(get_voltage(turbidityPin))
timeTurbNow = time.monotonic()
timeTurbPrev = timeTurbNow
turbDelay = 15  # delay in [s]

# Accelerometer sensor
accelerometer = adafruit_adxl34x.ADXL343(i2c)
accelerometer.enable_motion_detection(threshold=30)
# Motion status vars
timeMotionNow = time.monotonic()
timeMotionPrev = timeMotionNow
motionDelay = 1
motionNow = accelerometer.events['motion']

# GPS sensor
gps = adafruit_gps.GPS(uart, debug=False)
gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
gps.send_command(b"PMTK220,1000")

#For LCD Screen
cols = 16
rows = 2
lcd = character_lcd.Character_LCD_I2C(i2c,cols,rows)
lcd.backlight = True

# Flow sensor
flow = DigitalInOut(board.D5)
flow.direction = Direction.INPUT
flow.pull = Pull.DOWN
# Flow vars
timeFlowNow = time.monotonic()
timeFlowPrev = timeFlowNow
flowNow = flow.value
flowPrev = flow.value
edgeCounter = 0 # pulses
flowRate = 0    # flow rate in [L/min]
flowDelay = 1.0 # delay in [s]

# SD card
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")
with open("/sd/data.csv", "w") as f:
    f.write("Date/Time (UTC),Latitude (degrees),Longitude (degrees),Turbidity (NTU),Motion,Flow Rate (L/min)\r\n")
storage.umount(vfs)
# Data writing vars
timeSDNow = time.monotonic()
timeSDPrev = timeSDNow
SDDelay = 15    # delay in [s]

# Pump status vars
functional = True


timeNow = time.monotonic()
time4Hours = time.monotonic()
timePrev = timeNow


# Debugging vars
timeDebugNow = time.monotonic()
timeDebugPrev = timeDebugNow
debugDelay = .1
GPS_on = False

'''
-------------------- Main Loop --------------------
'''

while True:

    # GPS code
    if(GPS_on):
        gps.update()

        if not gps.timestamp_utc:
            print("No time data from GPS yet")


        if not gps.has_fix:
            print("Waiting for fix...")
            continue


        # time_gps = "{}/{}/{} {:02}:{:02}:{:02}".format(
    #             gps.timestamp_utc.tm_mon,
    #             gps.timestamp_utc.tm_mday,
    #             gps.timestamp_utc.tm_year,
    #             gps.timestamp_utc.tm_hour,
    #             gps.timestamp_utc.tm_min,
    #             gps.timestamp_utc.tm_sec,
    #         )
    #     print(time_gps)

        timeNow = time.monotonic();


        if ((timeNow - timePrev) > 300.0):
            print("{}/{}/{} {:02}:{:02}:{:02}".format(
                gps.timestamp_utc.tm_mon,
                gps.timestamp_utc.tm_mday,
                gps.timestamp_utc.tm_year,
                gps.timestamp_utc.tm_hour,
                gps.timestamp_utc.tm_min,
                gps.timestamp_utc.tm_sec,
            ))

            time_gps = "{}/{}/{} {:02}:{:02}:{:02}".format(
                gps.timestamp_utc.tm_mon,
                gps.timestamp_utc.tm_mday,
                gps.timestamp_utc.tm_year,
                gps.timestamp_utc.tm_hour,
                gps.timestamp_utc.tm_min,
                gps.timestamp_utc.tm_sec,
            )

            latitude = "{0:.6f}".format(gps.latitude)
            longitude = "{0:.6f}".format(gps.longitude)


            with open("/sd/testTimeNEW.csv", "a") as f:
                f.write(time_gps+","+latitude+","+longitude+"\r\n")

            timePrev = timeNow


    # Motion + Flow sensor code
    # Once motion is detected, measure flow rate
    motionNow = accelerometer.events['motion']
    if(motionNow):
        timeMotionNow = time.monotonic()

        if((timeMotionNow - timeMotionPrev) > motionDelay):
            print('Start motion')
            timeFlowNow = time.monotonic()
            timeFlowPrev = timeFlowNow
            flowNow = flow.value
            flowPrev = flowNow
            edgeCounter = 0

        while(motionNow):
            motionNow = accelerometer.events['motion']
            flowNow = flow.value
            if((flowNow != flowPrev) and flowNow):
                edgeCounter += 1
                print("increment")
            flowPrev = flowNow

            timeFlowNow = time.monotonic()
            if ((timeFlowNow - timeFlowPrev) > flowDelay):
                flowRate = pulse_to_volume(edgeCounter, flowDelay)
                functional = flowRate > 0
                print(edgeCounter)
                edgeCounter = 0
                print("Flow rate (L/min): "+ str(flowRate))
                timeFlowPrev = timeFlowNow

            timeMotionPrev = timeMotionNow
    else:
        flowRate = 0

    # Turbidity code
    # Wait for a little and measure turbidity
    timeTurbNow = time.monotonic()
    if((timeTurbNow - timeTurbPrev) > turbDelay):
        turbidityVal = volt_to_NTU(get_voltage(turbidityPin))
        print('Turbidity (NTU): ' + str(turbidityVal))

        timeTurbPrev = timeTurbNow

    # Print to LCD
    lcd.message = "Functional: " + ("Yes" if functional else "No ") + f"\nNTU: {turbidityVal:.2f}"

    # Write to SD card
    timeSDNow = time.monotonic()
    if((timeSDNow - timeSDPrev) > SDDelay):
        storage.mount(vfs, "/sd")
        if(GPS_on == False):
            time_gps = f"{time.monotonic():.f}"
            latitude = "0"
            longitude = "0"
        with open("/sd/data.csv", "a") as f:
            f.write(time_gps+","+latitude+","+longitude+","+str(turbidityVal)+","+str(motionNow)+","+str(flowRate)+"\r\n")
        storage.umount(vfs)

        timeSDPrev = timeSDNow

