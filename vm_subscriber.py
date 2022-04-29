"""EE 250L Lab 05 Starter Code

Run vm_subscriber.py in a separate terminal on your VM."""

import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to the ultrasonic ranger topic here
    client.subscribe("xchen335/ultrasonicRanger") #Maxc
    client.message_callback_add("xchen335/ultrasonicRanger", on_Ranger) #Maxc

    #subscribe to the button topic here
    client.subscribe("xchen335/button") #Maxc
    client.message_callback_add("xchen335/button", on_Button) #Maxc


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
            

