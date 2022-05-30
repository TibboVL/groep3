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
bd = BlueDot(cols=1, rows=2)

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
MAC2 = "E0:E2:E6:9B:A4:4E"
SERVICE_UUID = "ff1f7f47-ec50-4b76-9145-24527939bd0e"
SERVICE_UUID2 = "211c5eea-2899-4de3-80f9-e22344cb6019"


print("Connect to:" + MAC)

connectCount1 = 1
connectCount2 = 1

while True:
    try:
        dev = btle.Peripheral(MAC)
        break
    except:
        time.sleep(.2)
        connectCount1 += 1
        print(str(connectCount1) + "\t failed to connect to device 1...retrying")


while True:
    try:
        dev2 = btle.Peripheral(MAC2)
        break
    except:
        time.sleep(.2)
        connectCount2 += 1
        print(str(connectCount2) + "\t failed to connect to device 2...retrying")

print("connected succesfully!")

#uuids to connect to and read out
temperatureUUID = "a259ab92-cbe6-4412-b44f-0ef3e2247bcc"
temperatureUUID2 = "5d569488-3659-41f3-843e-fd1a862f2a89"

weightUUID = "4db28904-27f3-4379-89ad-321eafaec7ac"
weightUUID2 = "42480b98-e8fc-4cca-a8ea-85e828c658a2"

LightUUID = "71147fea-e715-479b-9a5a-5286b49d327c"
LightUUID2 = "8408d6f3-f644-4b3b-b0bc-224592d94094"


# get the service
service = dev.getServiceByUUID(SERVICE_UUID)
service2 = dev2.getServiceByUUID(SERVICE_UUID2)
#setup variables for all uuids
global Light
Light = dev.getCharacteristics(uuid=LightUUID)
global Light2
Light2 = dev2.getCharacteristics(uuid=LightUUID2)

temperature = dev.getCharacteristics(uuid=temperatureUUID)
temperature2 = dev2.getCharacteristics(uuid=temperatureUUID2)

weight = dev.getCharacteristics(uuid=weightUUID)
weight2 = dev2.getCharacteristics(uuid=weightUUID2)

#bluedot
def checkApp(name, delay, buttonnumber):
    global Light
    global Light2
    lampStatus = False
    while True:
        # wait for button press
        bd[0,buttonnumber].wait_for_press()

        if not lampStatus:
            lampStatus = True
            byte_message = bytes("ON", 'utf-8')
            if buttonnumber == 0:
                Light[0].write(byte_message)
            else:
                Light2[0].write(byte_message)
        else:
            lampStatus = False
            byte_message = bytes("OFF", 'utf-8')
            if buttonnumber == 0:
                Light[0].write(byte_message)
            else:
                Light2[0].write(byte_message)
        print("You pressed the blue dot!")

        if exit_event.is_set():
            break

checkApp = threading.Thread(target=checkApp, args=("Check App", 1, 0))
checkApp2 = threading.Thread(target=checkApp, args=("Check App", 1, 1))
## start thread
checkApp.start()
checkApp2.start()


try:
    while True:

        
        
        newtemperature = temperature[0].read().decode("utf-8") 
        print("Temperature = " + newtemperature + "°C")

        newtemperature2 = temperature2[0].read().decode("utf-8") 
        print("Temperature2 = " + newtemperature2 + "°C")

        
        newweight = weight[0].read().decode("utf-8") 
        print("Weight = " + newweight + "kg")

        newweight2 = weight2[0].read().decode("utf-8") 
        print("Weight2 = " + newweight2 + "kg")



        tempint = int(float(newtemperature))
        weightint = int(float(newweight))

        tempint2 = int(float(newtemperature2))
        weightint2 = int(float(newweight2))
        
        if weightint > 50:
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": "aig2regs2r564qwdkc1c21n6xqp99u",
                "user": "uzpzcow2pbfpsdiyw696197monf3rj",
                "message": "Hive 1 is too heavy!",
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()
        
        if weightint2 > 50:
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": "aig2regs2r564qwdkc1c21n6xqp99u",
                "user": "uzpzcow2pbfpsdiyw696197monf3rj",
                "message": "Hive 2 is too heavy!",
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()

        
        if tempint > 50:
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": "aig2regs2r564qwdkc1c21n6xqp99u",
                "user": "uzpzcow2pbfpsdiyw696197monf3rj",
                "message": "Hive 1 is too hot!",
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()
        
        if tempint2 > 50:
            conn = http.client.HTTPSConnection("api.pushover.net:443")
            conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": "aig2regs2r564qwdkc1c21n6xqp99u",
                "user": "uzpzcow2pbfpsdiyw696197monf3rj",
                "message": "Hive 2 is too hot!",
            }), { "Content-type": "application/x-www-form-urlencoded" })
            conn.getresponse()

        
        data= {
        "id": uid,
        "sensors":[
            {
	        'id': 'temperatuur hive 1',
	        'data': tempint
	        },
            {
	        'id': 'temperatuur hive 2',
	        'data': tempint2
	        },
            {
	        'id': 'weight hive 1',
	        'data': weightint
	        },
            {
	        'id': 'weight hive 2',
	        'data': weightint2
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

