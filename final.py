
"""EE 250L Final Project Code
Run vm_subscriber-maxcProj.py in a separate terminal on your VM."""

import paho.mqtt.client as mqtt
import time
import smtplib, ssl
from email.message import EmailMessage




def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))


    send_email("shinjsu92@gmail.com")
    send_email('sejohn@usc.edu')
    send_email('xchen335@usc.edu')

    #subscribe to the ultrasonic ranger topic here
    client.subscribe("xchen335/ultrasonicRanger") #Maxc
    client.message_callback_add("xchen335/ultrasonicRanger", on_Ranger) #Maxc

    #subscribe to the button topic here
    client.subscribe("xchen335/button") #Maxc
    client.message_callback_add("xchen335/button", on_Button) #Maxc

    #subscribe to the email topic here
    client.subscribe("xchen335/email") #Maxc
    client.message_callback_add("xchen335/email", on_Email) #Maxc


#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def on_Ranger(client, userdata, message): #Maxc rename from suctom_callback()
    #the third argument is 'message' here unlike 'msg' in on_message
    
    # Action for Ranger message is printing out the value.
    print("VM: " + str(message.payload, "utf-8") + " cm") #Maxc


def on_Button(client, userdata, message): #Maxc rename from suctom_callback()
    #the third argument is 'message' here unlike 'msg' in on_message
    
    # Action for Button message is printing out if the button pressed.
    print("VM: " + str(message.payload, "utf-8") ) #Maxc
    if (str(message.payload, "utf-8") == 'Y'):
        print("Button pressed!")
    else:
        print("Button not pressed!")


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

    

def on_Email(client, userdata, message): #Maxc rename from suctom_callback()
    #the third argument is 'message' here unlike 'msg' in on_message
    
    # Action for email message is printing out the string.
    print("Received email Info:" + str(message.payload, "utf-8") ) #Maxc
    send_email(str(message.payload, "utf-8"))
    send_email('sejohn@usc.edu')
    send_email('xchen335@usc.edu')


if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=1883, keepalive=60)
    client.loop_start()

    while True:
        #print("delete this line")
        #print("Waiting for the subscribed topic ...")
        time.sleep(1)

    
