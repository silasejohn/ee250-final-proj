"""EE 250L Final Project Code
Run vm_subscriber-maxcProj.py in a separate terminal on your VM."""

import paho.mqtt.client as mqtt
import time

#################
## Global Vars ##
#################
serialID = 0
serialID_gen = "masterNode/serialID"
serialIDACK = "masterNode/serialIDACK"
isSerialOpenForInit = True


def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code " + str(rc))

    client.subscribe(serialIDACK)
    client.message_callback_add(serialIDACK, on_generation_ACK)

    """
    #subscribe to the ultrasonic ranger topic here
    client.subscribe("parkingNode/ultrasonicRanger") #Maxc
    client.message_callback_add("parkingNode/ultrasonicRanger", on_Ranger) #Maxc

    # subscribe to the button topic here
    client.subscribe("parkingNode/button") #Maxc
    client.message_callback_add("parkingNode/button", on_Button) #Maxc

    # subscribe to the email topic here
    client.subscribe("parkingNode/email") #Maxc
    client.message_callback_add("parkingNode/email", on_Email) #Maxc
    """


#D efault message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def on_Ranger(client, userdata, message):    
    # Action for Ranger message is printing out the value.
    print("RangeFinder Value: " + str(message.payload, "utf-8") + " cm")

def on_generation_ACK(client, userdata, message):
    # action for recieving confirmation that serial ID is assigned
    global serialID
    global isSerialOpenForInit
    
    # code to check the ACK serialID, and increment it by one
    print("Current Serial ID: " + str(serialID))
    ack_message = str(message.payload, "utf-8")
    print("ACK Message: " + ack_message)
    serialID += 1
    print("New Serial ID: " + str(serialID))
    isSerialOpenForInit = True

"""
def on_Button(client, userdata, message):  
    # Action for Button message is printing out if the button pressed.
    if (str(message.payload, "utf-8") == 'Y'):
        print("Button pressed!")
    else:
        print("Button not pressed!")

def on_Email(client, userdata, message):     
    # Action for email message is printing out the string.
    print("Received email info:" + str(message.payload, "utf-8") ) #Maxc
"""

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=1883, keepalive=60)
    client.loop_start()

    while True:
        if(isSerialOpenForInit):
            client.publish(serialID_gen, str(serialID))
            isSerialOpenForInit = False
        time.sleep(.1)
