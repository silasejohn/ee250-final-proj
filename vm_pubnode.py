"""EE 250L Final Project Code
Run vm_publisher-maxcProj.py in a separate terminal on your VM."""

import paho.mqtt.client as mqtt
import time
from pynput import keyboard

#################
## GLOBAL VARS ##
#################

# subscriped topics 
serialIDGen = "masterNode/serialID"

# published topics
serialIDACK = "masterNode/serialIDACK"
operationalNode = "masterNode/operationalNode"

nodeName = "testNode"
node_serialID = None
isIDSetup = False # turns true once node serialID is given an integer
canRedefine = False

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code " + str(rc))
        
    # subscribe to the serialID generation topic here
    client.subscribe(serialIDGen) 
    print("Subscribed to master serial ID generation")
    client.message_callback_add(serialIDGen, on_generation) 

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

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
        print("Published ACK message to master SUB node")
        nodeName += node_serialID
        print("Name of this node main topic is: " + nodeName)
        isIDSetup = True
        canRedefine = True

def redefine_topic_names():
    # take all the original topic names and republish it with the new node name
    global operationalNode
    global nodeName
    operationalNode = nodeName + "/operationalNode"
    client.publish(operationalNode, nodeName + " is currently active")
    print("Published operational status to master subscription node")
    
"""
def on_press(key):
    try: 
        k = key.char # single-char keys
    except: 
        k = key.name # other keys
    
    if k == 'm':
        client.publish("parkingNode/lcd", "m")
        print("Added (hard reset) 25 cents")
        client.publish("parkingNode/credit", "25")
"""

if __name__ == '__main__':
    #setup the keyboard event listener
    # lis = keyboard.Listener(on_press=on_press)
    # lis.start() # start to listen on a separate thread

    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=1883, keepalive=60)
    client.loop_start()

    while True:
        if (isIDSetup and canRedefine):
            redefine_topic_names()
            canRedefine = False
            
        time.sleep(1)
            
