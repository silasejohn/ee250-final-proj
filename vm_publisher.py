"""EE 250L Lab 05 Starter Code

Run vm_publisher.py in a separate terminal on your VM."""

import paho.mqtt.client as mqtt
import time
from pynput import keyboard

def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

def on_press(key):
    try: 
        k = key.char # single-char keys
    except: 
        k = key.name # other keys
    
    if k == 'w':
        print("keyboard-w publised")
        #send "w" character to rpi
        client.publish("xchen335/lcd", "w")
    elif k == 'a':
        print("keyboard-a publised")
        # send "a" character to rpi
        client.publish("xchen335/lcd", "a")
        #send "LED_ON"
        client.publish("xchen335/led", "LED_ON")
    elif k == 's':
        print("keyboard-s publised")
        # send "s" character to rpi
        client.publish("xchen335/lcd", "s")
    elif k == 'd':
        print("keyboard-d publised")
        # send "d" character to rpi
        client.publish("xchen335/lcd", "d")
        # send "LED_OFF"
        client.publish("xchen335/led", "LED_OFF")

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
            

