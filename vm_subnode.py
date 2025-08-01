##########################
## EE 250 FINAL PROJECT ##
##########################
### Silas, Max, Joseph ###
##########################

""" RUN THIS FILE ON VM """

import paho.mqtt.client as mqtt
import time
import smtplib, ssl
from email.message import EmailMessage
import webbrowser

#################
## Global Vars ##
#################
serialID = 0
node_count = 10 # the number of nodes / parking spots that can be in the network, which can be expanded
                # we limited node count to 10 for testing purposes
isSerialIDChanged = True
nodeMoneyInserted = [0] * node_count # initialize the number of quarters per machine as 0
nodeStates = ["IDLE"] * node_count # stores the current state of node
carExistance = ["False"] * node_count # initialize the existances to false (or 0)
string_carExistance = ["Spot is Open"] * node_count # used for browser feed
emailList = [0] * node_count
default_email = 'sejohn@usc.edu'
local_webpage = ""

# published topics
serialID_gen = "masterNode/serialID"

# subscribed topics
serialIDACK = "masterNode/serialIDACK"

###############
## FUNCTIONS ##
###############

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
        subtopic_nodeState = "parkingNode" + str(counter) + "/nodeState" # topic that receives info on state of parking node
        client.subscribe(topic_nodeMoneyInserted)
        client.subscribe(subtopic_carExists)
        client.subscribe(subtopic_sendEmail)
        client.subscribe(subtopic_nodeState)
        print("Subscriped to Topic: " + topic_nodeMoneyInserted)
        print("Subscribed to Topic: " + subtopic_carExists)
        print("Subscribed to Topic: " + subtopic_sendEmail)
        print("Subscribed to Topic: " + subtopic_nodeState)
        client.message_callback_add(topic_nodeMoneyInserted, on_money_insert)
        client.message_callback_add(subtopic_carExists, on_car_existance)
        client.message_callback_add(subtopic_sendEmail, on_email)
        client.message_callback_add(subtopic_nodeState, on_node_recv)

        counter += 1

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
    global default_email
    message = str(message.payload, "utf-8")
    message_split = message.split(":")
    emailList[int(message_split[0])] = str(message_split[1]) # which nodes should send email (by index)
    if (bool(message_split[1])): # if should send email
        send_email(str(default_email)) # would normally replace with a method of inputting emails
    print("\n\n{Node " + message_split[0] + "} - send email signal is " + message + "\n") 

def on_node_recv(client, userdata, message):
    # actions when recieve a state change of a node
    global nodeStates
    message = str(message.payload, "utf-8")
    message_split = message.split(":")
    nodeStates[int(message_split[0])] = str(message_split[1])
    print("{Node " + message_split[0] + "} - state is " + message_split[1] + "\n")

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
        ## SET UP EMAIL SETTINGS HERE ##
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)
        ## ADD PERSONAL INFO ##
        sender_email = "park.notification123@gmail.com"
        receiver_email = to_email
        ## EMAIL CONTENT ##
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
        ## Send the ACTUAL email here ##
        server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
    # Print any error messages to stdout
        print(e)
    finally:
        server.quit()

# function to rewrite the page and html generated
def rewritePage():
    global local_webpage
    global carExistance
    global string_carExistance
    global nodeMoneyInserted

    # some calculations for things displayed on the webpage
    total_current_node_money = sum(nodeMoneyInserted)
    
    num_illegal_cars = 0
    for element in nodeStates:
        if (str(element) == 'LOADING'):
            num_illegal_cars += 1

    for element in range(len(carExistance)):
        if (str(carExistance[element]) == 'True'):
            string_carExistance[element] = "UNAVAILABLE"
        else: 
            string_carExistance[element] = "Spot is Open"

    # actual webpage html template code
    local_webpage = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title> Parking Lot Management System </title>
        <meta http-equiv="refresh" content="3">
    </head>
    <body>
        <h1>Parking Lot Management System</h1>
        <p>an MQTT-based system capable of monitoring parking lot space availability</p>
        <p>- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -</p>
        <p>NODE AVAILABILITY (whether a car is currently parked here or not):</p>
        <ul>
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
        <p>Total Money Inserted into Parking Meters Currently:&nbsp; """ + str(total_current_node_money) + """</p>
        <p>Number of Current Illegal Parking Cars: """ + str(num_illegal_cars) + """</p>
    </body>
    </html>
"""

# a function that helps display the html template on the browser (locally)
def browserDisplay():
    global local_webpage
    rewritePage()
    newLocalWebpage = open("displayData.html", "w")
    newLocalWebpage.write(local_webpage)
    newLocalWebpage.close()

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=1883, keepalive=60)
    client.loop_start()
    browserDisplay()
    webbrowser.open_new_tab("displayData.html")

    while True:
        # will continously be publishing newest serialID on the loop (newest node will pick it up)
        client.publish(serialID_gen, str(serialID)) 
        # if a serialID is assigned
        if(isSerialIDChanged):
            print("Published to Topic: " + serialID_gen + " with message of " + str(serialID))
            print("Scanning for next node ... ")
            isSerialIDChanged = False # becomes true when recieve a ACK message from the initialized new node
            time.sleep(.1)
        
        time.sleep(.1) # gives some break in the loop
        browserDisplay() # display / update the browser visualization