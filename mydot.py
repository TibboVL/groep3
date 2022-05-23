#!/usr/bin/env python3 
import cgitb ; cgitb.enable() 
import spidev 
import time
import busio
import digitalio
import board
import RPi.GPIO as GPIO 
from adafruit_bus_device.spi_device import SPIDevice

#user broadcom chip nummering
GPIO.setmode(GPIO.BCM)

#setup pins LED
GPIO.setup(4, GPIO.OUT,  initial=GPIO.HIGH) 

from bluedot import BlueDot
bd = BlueDot()
bd.wait_for_press()
GPIO.output(4, 0)
print("You pressed the blue dot!")