#!/usr/bin/env python3 
import cgitb ; cgitb.enable() 
import spidev 
import time
import busio
import digitalio
import board
from adafruit_bus_device.spi_device import SPIDevice
import RPi.GPIO as GPIO
# threading
import threading
exit_event = threading.Event()

# bluetooth control app
from bluedot import BlueDot
bd = BlueDot()

import http.client, urllib
conn = http.client.HTTPSConnection("api.pushover.net:443")
conn.request("POST", "/1/messages.json",
  urllib.parse.urlencode({
    "token": "aig2regs2r564qwdkc1c21n6xqp99u",
    "user": "uzpzcow2pbfpsdiyw696197monf3rj",
    "message": "Groep 3 Pi started",
  }), { "Content-type": "application/x-www-form-urlencoded" })
conn.getresponse()

# ubeac
import requests
url = "http://groep3.hub.ubeac.io/groep3"
uid = "groep3"

# Initialize SPI bus
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialize control pins for adc
cs0 = digitalio.DigitalInOut(board.CE0)  # chip select
adc = SPIDevice(spi, cs0, baudrate= 1000000)
 
#user broadcom chip nummering
GPIO.setmode(GPIO.BCM)

#setup pins LED
GPIO.setup(4, GPIO.OUT,  initial=GPIO.HIGH) 

# read SPI data 8 possible adc's (0 thru 7) 
def readadc(adcnum): 
	if ((adcnum > 7) or (adcnum < 0)): 
		return -1 
	with adc:
		r = bytearray(3)
		spi.write_readinto([1,(8+adcnum)<<4,0], r)
		time.sleep(0.000005)
		adcout = ((r[1]&3) << 8) + r[2] 
		return adcout 

	

def checkApp(name, delay):
    lampStatus = False
    while True:
        # wait for button press
        bd.wait_for_press()
        if not lampStatus:
            lampStatus = True
            GPIO.output(4, 0)
        else:
            lampStatus = False
            GPIO.output(4, 1)
        print("You pressed the blue dot!")

        if exit_event.is_set():
            break

checkApp = threading.Thread(target=checkApp, args=("Check App", 1))
## start thread
checkApp.start()

#ad_manager = dbus.Interface(adapter_obj, LE_ADVERTISING_MANAGER_IFACE)

try:

    while True:
        
        # take measurments
        temperature = readadc(0)/10 # read channel 0 
        weight = readadc(1)/10  # read channel 1
        print ("temperature:", temperature, "°C")
        print ("weight:", weight, "kg")

        if weight > 50:
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": "aig2regs2r564qwdkc1c21n6xqp99u",
                "user": "uzpzcow2pbfpsdiyw696197monf3rj",
                "message": "Hive is too heavy!",
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()

        if temperature > 50:
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": "aig2regs2r564qwdkc1c21n6xqp99u",
                "user": "uzpzcow2pbfpsdiyw696197monf3rj",
                "message": "Hive is too hot!",
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()

        data= {
        "id": uid,
        "sensors":[
            {
	        'id': 'temperatuur',
	        'data': temperature
	        },
            {
	        'id': 'weight',
	        'data': weight
	        }
            ]
        }
        r = requests.post(url, verify=False,  json=data)

        
        time.sleep(.5) #run main loop each second
	
except KeyboardInterrupt:
    exit_event.set()
    time.sleep(.25)
    GPIO.cleanup()