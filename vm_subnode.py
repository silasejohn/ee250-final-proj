"""EE 250L Final Project Code
Run vm_subscriber-maxcProj.py in a separate terminal on your VM."""

import paho.mqtt.client as mqtt
import time

#################
## Global Vars ##
#################
serialID = 0
isSerialIDChanged = True
nodeMoneyInserted = [0] * 10 # initilize the number of quarters per machine as 0
carExistance = [0] * 10 # initialize the existances to false (or 0)

# published topics
serialID_gen = "masterNode/serialID"

# subscribed topics
serialIDACK = "masterNode/serialIDACK"

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code " + str(rc))
    time.sleep(.1)

    client.subscribe(serialIDACK)
    print("Subscribed to Topic: " + serialIDACK)
    client.message_callback_add(serialIDACK, on_generation_ACK)

    #######################
    ## INIT FOR 10 NODES ##
    #######################
    counter = 0
    while (counter < 10):
        # topic that reports the status of an node (parking spot)
        topic_operationalNode = "testNode" + str(counter) + "/operationalNode"
        topic_nodeMoneyInserted = "testNode" + str(counter) + "/nodeMoneyInserted"
        subtopic_carExists = "parkingNode" + str(counter) + "/carExists"
        client.subscribe(topic_operationalNode)
        client.subscribe(topic_nodeMoneyInserted)
        client.subscribe(subtopic_carExists)
        print("Subscriped to Topic: " + topic_operationalNode)
        print("Subscriped to Topic: " + topic_nodeMoneyInserted)
        print("Subscribed to Topic: " + subtopic_carExists)
        client.message_callback_add(topic_operationalNode, on_operational_node)
        client.message_callback_add(topic_nodeMoneyInserted, on_money_insert)
        client.message_callback_add(subtopic_carExists, on_car_existance)

        counter += 1

    """
    # subscribe to the email topic here
    client.subscribe("parkingNode/email") #Maxc
    client.message_callback_add("parkingNode/email", on_Email) #Maxc
    """


# Default message callback (if we recieve messages for something we don't know how to deal with)
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

# action for recieving confirmation that serial ID is assigned
def on_generation_ACK(client, userdata, message):
    global serialID
    global isSerialIDChanged
    
    # check the ACK serialID and print to terminal
    print("Current Serial ID: " + str(serialID))
    ack_message = str(message.payload, "utf-8")
    print("INITIALIZED NEW NODE: " + ack_message)

    # increment serial ID
    serialID += 1
    print("\nNew Serial ID Value: " + str(serialID))
    isSerialIDChanged = True

# actions for when a quarter is inserted into a node parking meter
def on_money_insert(client, userdata, message):
    global nodeMoneyInserted
    message = str(message.payload, "utf-8")
    message_split = message.split(":")
    nodeMoneyInserted[int(message_split[0])] = int(message_split[1])
    for i in nodeMoneyInserted:
        print("money available is " + str(i))

def on_car_existance(client, userdata, message):
    global carExistance
    message = str(message.payload, "utf-8")
    message_split = message.split(":")
    carExistance[int(message_split[0])] = message_split[1]
    for i in carExistance:
        print("car exists is " + str(i))

"""
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
        # will continously be publishing serialID on the loop
        client.publish(serialID_gen, str(serialID)) 

        if(isSerialIDChanged):
            print("Published to Topic: " + serialID_gen + " with message of " + str(serialID))
            isSerialIDChanged = False # becomes true when recieve a ACK message from the initialized new node
            time.sleep(1)
        
        time.sleep(1) # gives some break in the loop
