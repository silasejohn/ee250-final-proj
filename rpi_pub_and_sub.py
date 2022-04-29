"""EE 250L Lab 05 Starter Code

Run rpi_pub_and_sub.py on your Raspberry Pi."""

import paho.mqtt.client as mqtt
import time

import sys
# By appending the folder of all the GrovePi libraries to the system path here,
# we are successfully `import grovepi`
sys.path.append('../../Software/Python/')
# This append is to support importing the LCD library.
sys.path.append('../../Software/Python/grove_rgb_lcd')

import grovepi

from grovepi import *
from grove_rgb_lcd import *

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here. Now there are two topics: xchen335/led and /lcd.
    client.subscribe("xchen335/led") #Maxc
    client.message_callback_add("xchen335/led", on_LED) #Maxc

    client.subscribe("xchen335/lcd") #Maxc
    client.message_callback_add("xchen335/lcd", on_LCD) #Maxc

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def on_LED(client, userdata, message): #Maxc rename from suctom_callback()
    #the third argument is 'message' here unlike 'msg' in on_message
    led = 3 # Port of the led installed

    print("Command: " + str(message.payload, "utf-8") ) #Maxc 
    if (str(message.payload, "utf-8") == 'LED_ON'):
        print("Let LED on!")
        digitalWrite(led,1)		# Send HIGH to switch on LED
    else:
        print("Let LED off!")
        digitalWrite(led,0)		# Send LOW to switch off LED

def on_LCD(client, userdata, message): #Maxc rename from suctom_callback()
    #the third argument is 'message' here unlike 'msg' in on_message
    
    print("Command: " + str(message.payload, "utf-8") ) #Maxc
    setRGB(50,128,128)
    setText("Received letter: %c"%(str(message.payload, "utf-8")))  

if __name__ == '__main__':
    button = 2 # Port of the button installed.
    ultras = 4 # Port of the ultrasonic installed.

    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=1883, keepalive=60)
    client.loop_start()

    while True:
        # print("delete this line")
        objDist = grovepi.ultrasonicRead(ultras)
        client.publish("xchen335/ultrasonicRanger", objDist)

        if (grovepi.digitalRead(button) == 1): # Press= 1. no press =0
            client.publish("xchen335/button", 'Y')
        else:
            client.publish("xchen335/button", 'N')         

        time.sleep(1)        

