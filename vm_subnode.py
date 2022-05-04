##########################
## EE 250 FINAL PROJECT ##
##########################
### Silas, Max, Joseph ###
##########################

""" RUN THIS FILE ON VM """

import paho.mqtt.client as mqtt
import time
import sqlite3

"""
CREATE TABLE sharks(id integer NOT NULL, 
                    name text NOT NULL, 
                    sharktype text NOT NULL, 
                    length integer NOT NULL);

Column Names:
id 
name 
sharktype
length

INSERT INTO sharks VALUES (1, "Sammy", "Greenland Shark", 427);

VIEW TABLES
SELECT * FROM sharks; // view whole table

SELECT * FROM sharks WHERE id IS 1; // display column where id = 1

ALTER TABLE sharks ADD COLUMN age integer; // add a column to the table 

UPDATE sharks SET age = 272 WHERE id=1; // set the age value for id = 1, shark table

DELETE FROM sharks WHERE age <= 200; // delete every row for this is true

CREATE TABLE endangered (id integer NOT NULL, status text NOT NULL);
INSERT INTO endangered VALUES (1,  "near threatened");


?? CODE ??

import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post')
            )

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post')
            )

connection.commit()
connection.close()

"""

#################
## Global Vars ##
#################
serialID = 0
node_count = 10 # the number of nodes / parking spots that can be in the network, which can be expanded
                # we limited node count to 10 for testing purposes
isSerialIDChanged = True
nodeMoneyInserted = [0] * node_count # initialize the number of quarters per machine as 0
carExistance = [0] * node_count # initialize the existances to false (or 0)

# published topics
serialID_gen = "masterNode/serialID"

# subscribed topics
serialIDACK = "masterNode/serialIDACK"

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code " + str(rc))
    time.sleep(.1)

    # subscribe to here acknowledgements from nodes that have recieved a serial ID
    client.subscribe(serialIDACK)
    print("Subscribed to Topic: " + serialIDACK)
    client.message_callback_add(serialIDACK, on_generation_ACK)

    #######################
    ## INIT FOR 10 NODES ##
    #######################
    counter = 0
    while (counter < node_count):
        topic_nodeMoneyInserted = "parkingNode" + str(counter) + "/nodeMoneyInserted" # topic that receives current moneyInserted in a node
        subtopic_carExists = "parkingNode" + str(counter) + "/carExists" # topic that receives information on whether a car is parked
        client.subscribe(topic_nodeMoneyInserted)
        client.subscribe(subtopic_carExists)
        print("Subscriped to Topic: " + topic_nodeMoneyInserted)
        print("Subscribed to Topic: " + subtopic_carExists)
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

# actions for when money is inserted into a parking node meter
def on_money_insert(client, userdata, message):
    global nodeMoneyInserted
    message = str(message.payload, "utf-8")
    message_split = message.split(":")
    nodeMoneyInserted[int(message_split[0])] = int(message_split[1])
    print("{Node " + message_split[0] + "} - total money available: " + str(message_split[1]))

# actions that occur when the state of car existance changes for a parking spot 
def on_car_existance(client, userdata, message):
    global carExistance
    message = str(message.payload, "utf-8")
    message_split = message.split(":")
    carExistance[int(message_split[0])] = message_split[1]
    print("{Node " + message_split[0] + "} - car status: " + str(message_split[1]))

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
        # will continously be publishing newest serialID on the loop (newest node will pick it up)
        client.publish(serialID_gen, str(serialID)) 

        if(isSerialIDChanged):
            print("Published to Topic: " + serialID_gen + " with message of " + str(serialID))
            isSerialIDChanged = False # becomes true when recieve a ACK message from the initialized new node
            time.sleep(.1)
        
        time.sleep(.1) # gives some break in the loop
