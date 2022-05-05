##########################
## EE 250 FINAL PROJECT ##
##########################
### Silas, Max, Joseph ###
##########################

""" RUN THIS FILE ON RASPBERRY PI """

from platform import node
import paho.mqtt.client as mqtt
import time
from datetime import datetime

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
movingAvgFilterLength = 7
moneyExists = False
carExists = False
isEmailSent = False
nodeState = "IDLE"
activationState = False
nodeName = "parkingNode"
node_serialID = None # inits to a number
isIDSetup = False # turns true once node serialID is given an integer
sampleCarGoneTime = True
pastCarExistancepoints = [0] * movingAvgFilterLength


# subscribed topics 
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

########################
### CUSTOM CALLBACKS ###
########################

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

#################
### MAIN CODE ###
#################

if __name__ == '__main__':
    ## Port Init ##
    buttonA = 2 # Port of the button A installed.
    ultras = 4 # Port of the ultrasonic installed.
    ledR = 3 # Port of the led installed
    ledG = 7 # Port of the led installed

    ## INIT LCD + LED ##
    digitalWrite(ledR,0)
    digitalWrite(ledG,0)
    setRGB(0, 0, 0)
    setText("")

    ## INIT MQTT CLIENT, CONNECT TO BROKER ##
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=1883, keepalive=60) # port=1883
    client.loop_start()

    # LCD Initialization Protocol ##
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
    displayText = "System is Ready\n" + nodeName
    previousText = displayText
    setText(displayText)
    displayText = "Welcome! \nOpen Spot"
    time.sleep(1)
    list_insert_counter = -1

    while True:
        ## Rangefinder Logic ##
        ## DETERMINING EXISTANCE OF CAR ##
        objDist = grovepi.ultrasonicRead(ultras)
        list_insert_counter += 1
        if (list_insert_counter >= movingAvgFilterLength):
            list_insert_counter = 0
        if (objDist > 1) and (objDist < 100):
            pastCarExistancepoints[list_insert_counter] = 1
            # carExists = True
            # carGoneTime = datetime.now()
        else:
            pastCarExistancepoints[list_insert_counter] = 0
            # if (sampleCarGoneTime): # a flag symbolizing if the car is first sensed to disappear
            #     carGoneTime = datetime.now() # sets a time counter from when the car if first sensed to disappear
            #     sampleCarGoneTime = False 
            # if ((datetime.now() - carGoneTime).total_seconds()):
            #     carExists = False
            #     sampleCarGoneTime = True
            # else:
            #     pass
        total = sum(pastCarExistancepoints)
        if (total >= 7):
            oldCarExists = carExists
            carExists = True
        else: 
            oldCarExists = carExists
            carExists = False
        if (oldCarExists is not carExists):
            pubtopic_carExists = nodeName + "/carExists"
            client.publish(pubtopic_carExists, node_serialID + ":" + str(carExists))
            print("Published Topic: " + pubtopic_carExists + " with message " + str(carExists))
        
        ## INPUT MONEY LOGIC ##
        if (grovepi.digitalRead(buttonA) == 1):
            if (totalMoneyInserted is 0):
                timePre = datetime.now()
            totalMoneyInserted += 25 # 25 cents
            pubtopic_nodeMoneyInserted = nodeName + "/nodeMoneyInserted"
            client.publish(pubtopic_nodeMoneyInserted, node_serialID + ":" + str(totalMoneyInserted))
            print("Published Topic: " + pubtopic_nodeMoneyInserted + " with a message of " + str(totalMoneyInserted))
        
        ## DETERMINES IF MONEY EXISTS ##
        if totalMoneyInserted > 0:
            moneyExists = True  
        else:
            moneyExists = False

        ## CALCULATES NEW STATE ##
        prevState = nodeState
        if ((prevState is "IDLE") and carExists):
            nodeState = "LOADING"
        elif ((prevState is "IDLE") and moneyExists and not carExists):
            nodeState = "EMPTY"
        elif ((prevState is "LOADING") and moneyExists):
            nodeState = "SAFE"
        elif ((prevState is "LOADING") and not carExists):
            nodeState = "IDLE"
        elif ((prevState is "SAFE") and not carExists and moneyExists):
            nodeState = "EMPTY"
        elif ((prevState is "SAFE") and not moneyExists):
            nodeState = "LOADING"
        elif ((prevState is "EMPTY") and not moneyExists):
            nodeState = "IDLE"
        else: 
            nodeState = prevState

        if nodeState is not prevState:
            print("Current State: " + nodeState)

        ## PERFORMS CERTAIN ACTIONS BASED ON STATE ##
        if (nodeState is "IDLE"):
            digitalWrite(ledR,0)
            digitalWrite(ledG,0)
            setRGB(50,128,128)
            displayText = "Welcome! \nOpen Spot"
        elif (nodeState is "LOADING"):
            digitalWrite(ledR,1)
            digitalWrite(ledG,0)
            setRGB(128, 0, 0)
            displayText = "Enter Money!!!"
        elif (nodeState is "SAFE"):
            digitalWrite(ledR,0)
            digitalWrite(ledG,1)
            setRGB(0, 128, 0)
            timeAllotted = totalMoneyInserted * .6
            timeDiff = (datetime.now()-timePre).total_seconds() 
            if (timeDiff > timeAllotted):  
                nodeState = "LOADING"
                totalMoneyInserted = 0 
            timeLeft = int(timeAllotted) - int(timeDiff)
            if ((timeLeft <= 10) and (isEmailSent is False)):
                pubtopic_sendEmail = nodeName + "/sendEmail"
                client.publish(pubtopic_sendEmail, node_serialID + ":" + str(True))
                print("Published Topic: " + pubtopic_sendEmail + " with a message of " + str(True))
                isEmailSent = True
            displayText = "Time Left:     \n" + str(timeLeft)
            setText_norefresh(displayText)
        elif (nodeState is "EMPTY"):
            digitalWrite(ledR,0)
            digitalWrite(ledG,1)
            setRGB(128, 128, 0)
            displayText = "Clearing Extra\nMoney . . ."
            setText(displayText)
            totalMoneyInserted = 0
            isEmailSent = False
            pubtopic_nodeMoneyInserted = nodeName + "/nodeMoneyInserted"
            client.publish(pubtopic_nodeMoneyInserted, node_serialID + ":" + str(totalMoneyInserted))
            print("Published Topic: " + pubtopic_nodeMoneyInserted + " with a message of " + str(totalMoneyInserted))
            time.sleep(3)
        
        ## DISPLAYS OUTPUT ON LCD ##
        if ((previousText is not displayText) and (nodeState is not "SAFE")):
            setText(displayText)

        previousText = displayText

        time.sleep(.01)