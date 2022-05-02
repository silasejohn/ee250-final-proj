"""EE 250L Final Project Code
Run vm_publisher-maxcProj.py in a separate terminal on your VM."""

import paho.mqtt.client as mqtt
import time
from pynput import keyboard

serialIDGen = "masterNode/serialID"
serialIDACK = "masterNode/serialIDACK"
node_serialID = None
isIDSetup = False

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code " + str(rc))
        
    # subscribe to the serialID generation topic here
    if (not isIDSetup):
        client.subscribe(serialIDGen) 
        client.message_callback_add(serialIDGen, on_generation) 

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def on_generation(client, userdata, message):   
    global node_serialID 
    node_serialID = str(message.payload, "utf-8")
    print("Master Serial ID Value: " + node_serialID)
    client.publish(serialIDACK, "ACK:" + node_serialID)
    isIDSetup = True


def on_press(key):
    try: 
        k = key.char # single-char keys
    except: 
        k = key.name # other keys
    
    if k == 'm':
        client.publish("parkingNode/lcd", "m")
        print("Added (hard reset) 25 cents")
        client.publish("parkingNode/credit", "25")


if __name__ == '__main__':
    #setup the keyboard event listener
    lis = keyboard.Listener(on_press=on_press)
    lis.start() # start to listen on a separate thread

    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=1883, keepalive=60)
    client.loop_start()

    while True:
        #print("delete this line")
        #print("Waiting for publishing...")
        time.sleep(1)
            
