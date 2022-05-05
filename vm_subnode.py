##########################
## EE 250 FINAL PROJECT ##
##########################
### Silas, Max, Joseph ###
##########################

""" RUN THIS FILE ON VM """

import paho.mqtt.client as mqtt
import time
import sqlite3
import smtplib, ssl
from email.message import EmailMessage
import webbrowser

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
string_carExistance = [0] * node_count # used for browser feed
emailList = [0] * node_count
global_counter = 0
local_webpage = ""

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
        subtopic_sendEmail = "parkingNode" + str(counter) + "/sendEmail" # topic that receives information on when to send email
        client.subscribe(topic_nodeMoneyInserted)
        client.subscribe(subtopic_carExists)
        client.subscribe(subtopic_sendEmail)
        print("Subscriped to Topic: " + topic_nodeMoneyInserted)
        print("Subscribed to Topic: " + subtopic_carExists)
        print("Subscribed to Topic: " + subtopic_sendEmail)
        client.message_callback_add(topic_nodeMoneyInserted, on_money_insert)
        client.message_callback_add(subtopic_carExists, on_car_existance)
        client.message_callback_add(subtopic_sendEmail, on_email)

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
    if (message_split[1]):
        print("{Node " + message_split[0] + "} - ALL MONEY IS CLEARED (no car)")
    print("{Node " + message_split[0] + "} - total money available: " + str(message_split[1]))

# actions that occur when the state of car existance changes for a parking spot 
def on_car_existance(client, userdata, message):
    global carExistance
    message = str(message.payload, "utf-8")
    message_split = message.split(":")
    carExistance[int(message_split[0])] = message_split[1]
    print("{Node " + message_split[0] + "} - car status: " + str(message_split[1]))


def on_email(client, userdata, message):     
    # Action for email message is printing out the string.
    global emailList
    message = str(message.payload, "utf-8")
    message_split = message.split(":")
    #if (bool(message_split[1])):
    #    send_email(str(emailList[int(message_split[0])]))
    print("\n\n{Node " + message_split[0] + "} - send email signal is " + message + "\n") 
    send_email('sejohn@usc.edu')

def send_email(to_email):
# Try to log in to server and send email
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "park.notification123@gmail.com"
    password = "ee250!@#"
    # Create a secure SSL context
    context = ssl.create_default_context()
    
    print(to_email)
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)
        # TODO: Send email here
        sender_email = "park.notification123@gmail.com"
        receiver_email = to_email
        print("this is the email its sending to: " + to_email)
        print("sending email nowww")

        msg = EmailMessage()
        msg.set_content('Hello,                                \n' + 
        'This is a friendly reminder that your time is almost up \n' +
        'Please move your car before you run out of time or add more money to keep the car in the place.\n'+
        '\n'
        '\n'
        'Very Respectfully, \n'
        'USC EE250 Parking team \n')
        msg['Subject'] = 'Friendly Reminder: Time is almost out'
        msg['From'] = "USC EE250 Parking Enforcement"
        msg['To'] = to_email
                

    # Send email here
        server.sendmail(sender_email, receiver_email, msg.as_string())

    except Exception as e:
    # Print any error messages to stdout
        print(e)
    finally:
        server.quit()

def rewritePage():
    global local_webpage
    global carExistance
    global string_carExistance

    for element in range(len(carExistance)):
        if carExistance[element] is str(True):
            string_carExistance[element] = "Spot Open"
        else: 
            string_carExistance[element] = "UNAVAILABLE"

    local_webpage = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title> Parking Lot Management System </title>
        <meta http-equiv="refresh" content="6">
    </head>
    <body>
        <h1>Parking Lot Management System</h1>
        <p>an MQTT-based system capable of monitoring parking lot space availability</p>
        <p>- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -</p>
        <p>NODE AVAILABILITY (whether a car is currently parked here or not):</p>
        <ul>
            <li>{EXAMPLE NODE} ~&gt; AVAILABILITY : Paid XX&nbsp;</li>
            <li>{NODE ZERO} ~&gt; """ + string_carExistance[0] + """</li>
            <li>{NODE ONE} ~&gt; """ + string_carExistance[1] + """</li>
            <li>{NODE TWO}&nbsp;~&gt; """ + string_carExistance[2] + """</li>
            <li>{NODE THREE}&nbsp;~&gt; """ + string_carExistance[3] + """</li>
            <li>{NODE FOUR}&nbsp;~&gt; """ + string_carExistance[4] + """</li>
            <li>{NODE FIVE}&nbsp;~&gt; """ + string_carExistance[5] + """</li>
            <li>{NODE SIX}&nbsp;~&gt; """ + string_carExistance[6] + """</li>
            <li>{NODE SEVEN}&nbsp;~&gt; """ + string_carExistance[7] + """</li>
            <li>{NODE EIGHT}&nbsp;~&gt; """ + string_carExistance[8] + """</li>
            <li>{NODE NINE}&nbsp;~&gt; """ + string_carExistance[9] + """</li>
        </ul>
        <p>Total Money Inserted into Parking Meters Currently:&nbsp;</p>
        <p>Number of Current Illegal Parking Cars:</p>
        <p>Here is some&nbsp;<strong>sample bold text</strong>.&nbsp;</p>
        <blockquote>Here is a blockquote... add some more text!</blockquote>
    </body>
    </html?
"""

def browserDisplay():
    global local_webpage
    rewritePage()
    newLocalWebpage = open("displayData.html", "w")
    newLocalWebpage.write(local_webpage)
    newLocalWebpage.close()
    # webbrowser.open_new_tab("displayData.html")

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=1883, keepalive=60)
    client.loop_start()
    time_counter = 0
    browserDisplay()
    webbrowser.open_new_tab("displayData.html")

    while True:
        # will continously be publishing newest serialID on the loop (newest node will pick it up)
        client.publish(serialID_gen, str(serialID)) 

        if(isSerialIDChanged):
            print("Published to Topic: " + serialID_gen + " with message of " + str(serialID))
            isSerialIDChanged = False # becomes true when recieve a ACK message from the initialized new node
            time.sleep(.1)
        
        time.sleep(.1) # gives some break in the loop
        time_counter += 1
        browserDisplay()
        if (time_counter > 100):
            time_counter = 0
            global_counter += 1
            # browserDisplay()
