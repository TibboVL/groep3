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


MAC = "E0:E2:E6:9D:0F:DA"
MAC2 = "E0:E2:E6:9B:A4:4E"


#uuids to connect to and read out
temperatureUUID = "a259ab92-cbe6-4412-b44f-0ef3e2247bcc"
temperatureUUID2 = "5d569488-3659-41f3-843e-fd1a862f2a89"

weightUUID = "4db28904-27f3-4379-89ad-321eafaec7ac"
weightUUID2 = "42480b98-e8fc-4cca-a8ea-85e828c658a2"

LightUUID = "71147fea-e715-479b-9a5a-5286b49d327c"
LightUUID2 = "8408d6f3-f644-4b3b-b0bc-224592d94094"

global Light
global Light2

connectCount1 = 0
connectCount2 = 0

print("Connecting to device 1: " + MAC)
while True:
    try:
        dev = btle.Peripheral(MAC)
        temperature = dev.getCharacteristics(uuid=temperatureUUID)
        Light = dev.getCharacteristics(uuid=LightUUID)
        weight = dev.getCharacteristics(uuid=weightUUID)
        break
    except:
        time.sleep(.2)
        connectCount1 += 1
        print(str(connectCount1) + "\t failed to connect to device 1 ... retrying")

print("connected to device 1: " + MAC)
print("Connecting to device 2: " + MAC2)
while True:
    try:
        dev2 = btle.Peripheral(MAC2)
        Light2 = dev2.getCharacteristics(uuid=LightUUID2)
        temperature2 = dev2.getCharacteristics(uuid=temperatureUUID2)
        weight2 = dev2.getCharacteristics(uuid=weightUUID2)
        break
    except:
        time.sleep(.2)
        connectCount2 += 1
        print(str(connectCount2) + "\t failed to connect to device 2 ... retrying")

print("connected to device 2: " + MAC)
print("connected to both devices succesfully!")

#bluedot
def checkApp(name, delay):
    global Light
    lampStatus = False
    while True:
        # wait for button press
        bd[0,0].wait_for_press()
        print("You pressed button 1")
        if not lampStatus:
            lampStatus = True
            byte_message = bytes("ON", 'utf-8')
            Light[0].write(byte_message)
        else:
            lampStatus = False
            byte_message = bytes("OFF", 'utf-8')
            Light[0].write(byte_message)
        
        if exit_event.is_set():
            break

def checkApp2(name, delay):
    global Light2
    lampStatus = False
    while True:
        # wait for button press
        bd[0,1].wait_for_press()
        print("You pressed button 2" )
        if not lampStatus:
            lampStatus = True
            byte_message = bytes("ON", 'utf-8')
            Light2[0].write(byte_message)
        else:
            lampStatus = False
            byte_message = bytes("OFF", 'utf-8')
            Light2[0].write(byte_message)
        
        if exit_event.is_set():
            break

checkApp = threading.Thread(target=checkApp, args=("Check App 1", 1))
checkApp2 = threading.Thread(target=checkApp2, args=("Check App 2", 1))
## start thread
checkApp.start()
checkApp2.start()


try:
    while True:
        #dev.connect(MAC)
        #dev2.connect(MAC2)
        
        print("\nHive1: \n---------------------")
        newtemperature = temperature[0].read().decode("utf-8") 
        print("Temperature: \t" + newtemperature[:-3] + "°C")

        newweight = weight[0].read().decode("utf-8") 
        print("Weight: \t" + newweight[:-3] + "kg")

        print("\nHive2: \n---------------------")
        newtemperature2 = temperature2[0].read().decode("utf-8") 
        print("Temperature: \t" + newtemperature2[:-3] + "°C")

        newweight2 = weight2[0].read().decode("utf-8") 
        print("Weight: \t" + newweight2[:-3] + "kg")



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
        

        time.sleep(.5)
            
except KeyboardInterrupt:
    dev.disconnect()
    dev2.disconnect()
    exit_event.set()
    time.sleep(.25)
    GPIO.cleanup()

