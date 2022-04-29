"""EE 250L Lab 05 Starter Code

Run rpi_pub_and_sub.py on your Raspberry Pi."""

import paho.mqtt.client as mqtt
import time
from datetime import datetime

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
    buttonA = 2 # Port of the button A installed.
    ultras = 4 # Port of the ultrasonic installed.
    potentiometer = 2 # Analog port 2, see Lab6 code.
    ledR = 3 # Port of the led installed
    ledG = 1 # Port of the led installed
    emails = ["xchen335@usc.edu", "abc-1@usc.edu", "abc-2@usc.edu", "abc-3@usc.edu", "abc-4@usc.edu"]

    occupy = False
    moneyLeft = 0 # unit: cent
    moneyCredit = 0 # Subscribe the online payment info from the Center
    rate = 5.0 # 5 cent /min for parking rate
    timeExpir = 0
    timePre = datetime.now()

    state = "Idle" # total 5 states: Idle, Loading, Safe, Empty, Illegal
    newstate = "Idle"
    time1MCnt = 0 # 1 minute timer counter.

    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=1883, keepalive=60) # port=1883
    client.loop_start()

    setRGB(50,128,128)
    setText("EE250 FinalProj\nJoseph Silas Max")
    digitalWrite(ledR,1)		# self checking
    digitalWrite(ledG,1)		# 
    time.sleep(5)
    digitalWrite(ledR,0)		# self checking
    digitalWrite(ledG,0)		# 

    while True:
        objDist = grovepi.ultrasonicRead(ultras)
        if (objDist > 1) and (objDist <100) :
            occupy = True
        else :
            occupy = False
        timeNow = datetime.now()
        if moneyLeft:
            if (timeNow != timePre ) :
                moneyLeft = moneyLeft - rate*(timeNow-timePre).total_seconds() / 60
                #minutes_diff = (datetime_end - datetime_start).dt.total_seconds() / 60.0
                timePre = timeNow
                if moneyLeft<0:
                    moneyLeft = 0
        if (grovepi.digitalRead(buttonA) == 1):
            moneyLeft = moneyLeft + 25        
        timeLeft = (moneyCredit + moneyLeft)/rate
        moneyCredit = 0
        setText("MoneyL:%3d cnts\nDist: %3d cm"%(moneyLeft, objDist))
        time.sleep(1)

# State Machine Logic:
        if state == "Idle":
            setRGB(0,0,0)
            digitalWrite(ledR,0)		# Send Low to switch off Red LED
            digitalWrite(ledG,0)		# Send Low to switch off Green LED
            if occupy :
                newstate = "Loading"
            elif moneyLeft:
                newstate = "Empty"
        
        elif state == "Loading":
            setRGB(50,128,128)
            setText("Coin and Email:")
            digitalWrite(ledR,1)		# Send High to switch on Red LED 
            digitalWrite(ledG,1)            
            # check the potentiiometer value: total 5 different emails.
            potenVal = grovepi.analogRead(potentiometer)
            emailIndex = potenVal // 210
            email = emails[emailIndex]
            setText("Time left: \n%4d min"%(timeLeft))
            if (time1MCnt > 5) :
                time1MCnt = 0
                if (occupy and (moneyLeft !=0)):
                    newstate = "Safe" 
                    setText("Email: \n%s "%(email))
                    time.sleep(1)
                    #client.publish("xchen335/email", email) #Publish the email info (need timestart?)
                elif (occupy and (moneyLeft ==0)):
                    newstate = "Illegal"
                    #client.publish("xchen335/email", "fine") #Publish the email info ("fine means take ticket")
                elif (not occupy) and (moneyLeft !=0):
                    #client.publish("xchen335/email", "null") #Publish the email info ("null means remove the email")
                    newstate = "Empty"
                else :
                    newstate = "Idle"
        
        elif state == "Safe":
            digitalWrite(ledG,1)		# Send High to switch on Green LED
            digitalWrite(ledR,0) 
            setText("Time left: \n%4d min"%(timeLeft))
            if (occupy and (moneyLeft ==0)):
                newstate = "Loading"
            elif ((not occupy) and (moneyLeft !=0)):
                #client.publish("xchen335/email", "null") #Publish the email info ("null means remove the email")
                newstate = "Empty"
            elif ((not occupy) and (moneyLeft ==0)): 
                newstate = "Idle"
        
        elif state == "Empty":
            digitalWrite(ledG,1)		# Send High to switch on Green LED
            digitalWrite(ledR,0) 
            setText("Time left: \n%4d min"%(timeLeft))
            if (occupy and (moneyLeft ==0)):
                newstate = "Loading"
            elif ((not occupy) and (moneyLeft ==0)):
                newstate = "Idle"
            elif (occupy and (moneyLeft !=0)): 
                newstate = "Loading"        

        elif state == "Illegal":
            digitalWrite(ledR,1)		# Flash Red LED
            digitalWrite(ledG,0) 
            time.sleep(0.5)
            digitalWrite(ledR,0)
            setText("Please move")
            if (occupy and (moneyLeft !=0)):
                newstate = "Safe"
            elif ((not occupy) and (moneyLeft ==0)):
                newstate = "Idle"
            elif ((not occupy) and (moneyLeft !=0)): 
                newstate = "Empty"  
#End of the Logic.
        setText("State: %s\n NewSta: %s"%(state, newstate))
        if (state != newstate) :
            state = newstate
        elif (state == "Loading") :
            time1MCnt = time1MCnt +1
        



        
        # print("delete this line") Below is from Lab5
        objDist = grovepi.ultrasonicRead(ultras)
        client.publish("xchen335/ultrasonicRanger", objDist)

        if (grovepi.digitalRead(buttonA) == 1): # Press= 1. no press =0
            client.publish("xchen335/button", 'Y')
        else:
            client.publish("xchen335/button", 'N')         

        time.sleep(1)        

