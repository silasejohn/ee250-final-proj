"""EE 250L Final Project Code
Run rpi_pub_and_sub-maxcProj.py on Raspberry Pi."""

from platform import node
import paho.mqtt.client as mqtt
import time
from datetime import datetime

"""
State Machine
Insert Quarters

If button is pressed, add one quarter


"""

###############
### IMPORTS ### 
###############

import sys
# By appending the folder of all the GrovePi libraries to the system path here,
# we are successfully `import grovepi`
sys.path.append('../../Software/Python/')
# This append is to support importing the LCD library.
sys.path.append('../../Software/Python/grove_rgb_lcd')
import grovepi
from grovepi import *
from grove_rgb_lcd import *

###############
# Global Vars #
###############
totalMoneyInserted = 0
moneyExists = False
carExists = False
nodeState = "IDLE"
activationState = False
nodeName = "parkingNode"
node_serialID = None # inits to a number
isIDSetup = False # turns true once node serialID is given an integer

# subscriped topics 
serialIDGen = "masterNode/serialID"

# published topics
serialIDACK = "masterNode/serialIDACK"

###############
## Functions ##
###############

def on_connect(client, userdata, flags, rc):
    # subscribe to the serialID generation topic here
    client.subscribe(serialIDGen)
    print("Subscribed to master serial ID generation")
    client.message_callback_add(serialIDGen, on_generation)

# Default message callback # 
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

# custom callbacks go here # 

# generation code only happens once
def on_generation(client, userdata, message):
    global isIDSetup
    global nodeName
    global canRedefine
    if (not isIDSetup):
        global node_serialID 
        node_serialID = str(message.payload, "utf-8")
        print("Node Serial ID Value: " + node_serialID)
        client.publish(serialIDACK, "ACK:" + node_serialID)
        print("Published to Topic: " + serialIDACK + " with message of " + "ACK:" + node_serialID)            
        nodeName += node_serialID
        print("Name of this node main topic is: " + nodeName)
        isIDSetup = True

"""
def inputMoney():
    # Button Logic #
    global totalMoneyInserted
    if (grovepi.digitalRead(buttonA) == 1):
        totalMoneyInserted += 25 
        setText("\nInput Money: " + str(totalMoneyInserted))
        pubtopic_nodeMoneyInserted = nodeName + "/nodeMoneyInserted"
        client.publish(pubtopic_nodeMoneyInserted, node_serialID + ":" + str(totalMoneyInserted))
        print("Published Topic: " + pubtopic_nodeMoneyInserted + " with a message of " + str(totalMoneyInserted))
"""

if __name__ == '__main__':
    buttonA = 2 # Port of the button A installed.
    ultras = 4 # Port of the ultrasonic installed.
    potentiometer = 2 # Analog port 2, see Lab6 code.
    ledR = 3 # Port of the led installed
    ledG = 7 # Port of the led installed
    # emails = ["xchen335@usc.edu", "abc-1@usc.edu", "abc-2@usc.edu", "abc-3@usc.edu", "abc-4@usc.edu"]

    digitalWrite(ledR,0)
    digitalWrite(ledG,0)
    setRGB(0, 0, 0)
    setText("")

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

    # LCD Initialization Text #
    setRGB(50,128,128) # set to light blue
    setText("EE 250\nFinal Project")
    time.sleep(2)
    setText("Group Members: \nJoseph Silas Max")
    time.sleep(2)
    setRGB(0,128,0) # set to GREEN
    setText("Initializing\nLED ON")
    digitalWrite(ledR,1)		# self checking
    digitalWrite(ledG,1)
    time.sleep(2)		
    setRGB(128,0,0) # set to RED
    setText("Initializing\nLED OFF")
    digitalWrite(ledR,0)		# self checking
    digitalWrite(ledG,0)	
    time.sleep(1)    
    setRGB(50,128,128) # set to light blue
    setText("System is Ready\n" + nodeName)
    time.sleep(1)

    time_counter = 0
    while True:
        # calculate car exists and money exists # 

        # Rangefinder Logic #
        objDist = grovepi.ultrasonicRead(ultras)
        oldCarExists = carExists
        if (objDist > 1) and (objDist < 100):
            carExists = True
        else:
            carExists = False
        if (oldCarExists is not carExists):
            pubtopic_carExists = "parkingNode" + node_serialID + "/carExists"
            client.publish(pubtopic_carExists, node_serialID + ":" + str(carExists))
            print("Published Topic: " + pubtopic_carExists + " with message " + str(carExists))
        
        # Button Logic #
        if (grovepi.digitalRead(buttonA) == 1):
            if (totalMoneyInserted is 0):
                timePre = datetime.now()
            totalMoneyInserted += 25 
            setText("\nInput Money: " + str(totalMoneyInserted))
            pubtopic_nodeMoneyInserted = nodeName + "/nodeMoneyInserted"
            client.publish(pubtopic_nodeMoneyInserted, node_serialID + ":" + str(totalMoneyInserted))
            print("Published Topic: " + pubtopic_nodeMoneyInserted + " with a message of " + str(totalMoneyInserted))
        
        if totalMoneyInserted > 0:
            moneyExists = True  
        else:
            moneyExists = False

        # state calculation logic #
        prevState = nodeState
        if ((prevState is "IDLE") and carExists):
            nodeState = "LOADING"
        elif ((prevState is "IDLE") and moneyExists):
            nodeState = "EMPTY"
        elif ((prevState is "LOADING") and moneyExists):
            nodeState = "SAFE"
        elif ((prevState is "LOADING") and not carExists):
            nodeState = "IDLE"
        elif ((prevState is "SAFE") and not carExists):
            nodeState = "EMPTY"
        elif ((prevState is "SAFE") and not moneyExists):
            nodeState = "LOADING"
        elif ((prevState is "EMPTY") and not moneyExists):
            nodeState = "IDLE"
        else: 
            nodeState = prevState

        print("Current State: " + nodeState)

        if (nodeState is "IDLE"):
            digitalWrite(ledR,0)
            digitalWrite(ledG,0)
            setRGB(50,128,128)
            setText("Welcome! \nOpen Spot")
        elif (nodeState is "LOADING"):
            digitalWrite(ledR,1)
            digitalWrite(ledG,0)
            setRGB(128, 0, 0)
            setText("Enter Money!!!")
        elif (nodeState is "SAFE"):
            digitalWrite(ledR,0)
            digitalWrite(ledG,1)
            setRGB(0, 128, 0)
            timeAllotted = totalMoneyInserted * 10
            timeDiff = (datetime.now()-timePre).total_seconds()
            if (timeDiff > timeAllotted):  
                nodeState = "LOADING"
                totalMoneyInserted = 0 
            timeLeft = timeAllotted - timeDiff
            setText("Time Left: " + str(timeLeft))
            # display time left
        elif (nodeState is "EMPTY"):
            digitalWrite(ledR,0)
            digitalWrite(ledG,1)
            setRGB(128, 128, 0)
            setText("Clearing Extra\nMoney . . .")
            time.sleep(3)
            totalMoneyInserted = 0


        time.sleep(.01)
        time_counter += 1
        if (time_counter >= 10):
            time_counter = 0
        """
        objDist = grovepi.ultrasonicRead(ultras)
        if (objDist > 1) and (objDist <100) :
            occupy = True
        else :
            occupy = False
        timeNow = datetime.now()
        if moneyLeft:
            if (timeNow != timePre ) :
                moneyLeft = moneyLeft - rate*(timeNow-timePre).total_seconds() / 60
                timePre = timeNow
                if moneyLeft<0:
                    moneyLeft = 0
        if (grovepi.digitalRead(buttonA) == 1):
            moneyLeft = moneyLeft + 25        
        if moneyCredit:
            moneyLeft = moneyCredit + moneyLeft
            moneyCredit = 0
            timeLeft = moneyLeft/rate
            client.publish("parkingNode/email", "ACK"+":"+str(int(timeLeft))+":"+state) #The ACK for the online payment.
        timeLeft = moneyLeft/rate + 1
        if moneyLeft==0 :
            timeLeft = 0

        #setText("MoneyL:%3d cnts\nDist: %3d cm"%(moneyLeft, objDist))
        #time.sleep(1)

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
            time.sleep(2)
            digitalWrite(ledR,1)		# Send High to switch on Red LED 
            digitalWrite(ledG,1)            
            # check the potentiiometer value: total 5 different emails.
            potenVal = grovepi.analogRead(potentiometer)
            emailIndex = potenVal // 210
            email = emails[emailIndex]
            print("Selecting Email: " + email)
            setText("Time left: \n%4d min"%(timeLeft))
            time.sleep(2)
            if (time1MCnt > 6) :
                time1MCnt = 0
                if (occupy and (moneyLeft !=0)):
                    newstate = "Safe" 
                    #setText("Email: \n%s "%(email))
                    #time.sleep(1)
                    print("Sent Email: " + email)
                    client.publish("parkingNode/email", email+":"+str(int(timeLeft))+":"+newstate) #Publish the email info (need timestart?)
                elif (occupy and (moneyLeft ==0)):
                    newstate = "Illegal"
                    client.publish("parkingNode/email", email+":fine"+":"+newstate) #Publish the email info ("fine means take ticket")
                elif (not occupy) and (moneyLeft !=0):
                    newstate = "Empty"
                    client.publish("parkingNode/email", email+":null"+":"+newstate) #Publish the email info ("null means remove the email")
                else :
                    newstate = "Idle"
        
        elif state == "Safe":
            digitalWrite(ledG,1)		# Send High to switch on Green LED
            digitalWrite(ledR,0) 
            setText("Time left: \n%4d min"%(timeLeft))
            if (occupy and (moneyLeft ==0)):
                newstate = "Loading"
            elif ((not occupy) and (moneyLeft !=0)):
                newstate = "Empty"
                client.publish("parkingNode/email", email+":null"+":"+newstate) #Publish the email info ("null means remove the email")                
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
            time.sleep(2)
            if (occupy and (moneyLeft !=0)):
                newstate = "Safe"
            elif ((not occupy) and (moneyLeft ==0)):
                newstate = "Idle"
            elif ((not occupy) and (moneyLeft !=0)): 
                newstate = "Empty"  
#End of the Logic.
        #setText("State: %s\n NewSta: %s"%(state, newstate))
        #print("State: " + state + " Newstate: " + newstate)
        if (state != newstate) :
            print("State: " + state + " Newstate: " + newstate)
            state = newstate
        elif (state == "Loading") :
            time1MCnt = time1MCnt +1
        



        
        # print("delete this line") Below is from Lab5
        # objDist = grovepi.ultrasonicRead(ultras)
        # client.publish("xchen335/ultrasonicRanger", objDist)
        # if (grovepi.digitalRead(buttonA) == 1): # Press= 1. no press =0
        #     client.publish("xchen335/button", 'Y')
        # else:
        #     client.publish("xchen335/button", 'N')        
        """   
