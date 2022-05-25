from bluepy import btle
import time
import cgitb ; cgitb.enable() 
import spidev
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


# BLE
MAC = "E0:E2:E6:9D:0F:DA"
SERVICE_UUID = "ff1f7f47-ec50-4b76-9145-24527939bd0e"

print("Connect to:" + MAC)

connectCount = 1

while True:
    try:
        dev = btle.Peripheral(MAC)
        break
    except:
        time.sleep(.2)
        connectCount += 1
        print(str(connectCount) + "\t failed to connect...retrying")

print("connected succesfully!")

temperatureUUID = "a259ab92-cbe6-4412-b44f-0ef3e2247bcc"
weightUUID = "4db28904-27f3-4379-89ad-321eafaec7ac"
LightUUID = "71147fea-e715-479b-9a5a-5286b49d327c"

service = dev.getServiceByUUID(SERVICE_UUID)


def checkApp(name, delay):
    lampStatus = False
    while True:
        # wait for button press
        bd.wait_for_press()
        if not lampStatus:
            lampStatus = True
            Light = dev.getCharacteristics(uuid=LightUUID)
            Light = Light.write("ON")
            GPIO.output(4, 0)
        else:
            lampStatus = False
            Light = Light.write("OFF")
            GPIO.output(4, 1)
        print("You pressed the blue dot!")

        if exit_event.is_set():
            break

checkApp = threading.Thread(target=checkApp, args=("Check App", 1))
## start thread
checkApp.start()


try:
    while True:

        #Light = dev.getCharacteristics(uuid=LightUUID)

        temperature = dev.getCharacteristics(uuid=temperatureUUID)
        temparature = temperature[0].read().decode("utf-8") 
        #print(type(temparature))
        print("Temperature = " + temparature + "°C")

        weight = dev.getCharacteristics(uuid=weightUUID)
        weight = weight[0].read().decode("utf-8") 
        #print(type(temparature))
        print("Weight = " + weight + "kg")

        tempint = int(float(temparature))
        weightint = int(float(weight))
        
        if weightint > 50:
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": "aig2regs2r564qwdkc1c21n6xqp99u",
                "user": "uzpzcow2pbfpsdiyw696197monf3rj",
                "message": "Hive is too heavy!",
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()

        
        if tempint > 50:
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
	        'data': tempint
	        },
            {
	        'id': 'weight',
	        'data': weightint
	        }
            ]
        }
        r = requests.post(url, verify=False,  json=data)
        

        time.sleep(.3)
            
except KeyboardInterrupt:
    dev.disconnect()
    exit_event.set()
    time.sleep(.25)
    GPIO.cleanup()

