#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522_p3
import signal
import time


reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global reading
    print("Ctrl+C captured, ending read.")
    reading = False
    GPIO.cleanup()
    
# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
rfid = MFRC522_p3.MFRC522()

# Welcome message
print("Welcome to the MFRC522 data read example")
print("Press Ctrl-C to stop.")

while reading:
    (status, TagType) = rfid.MFRC522_Request(rfid.PICC_REQIDL)
    
    if status == rfid.MI_OK:
        print("Card detected")
        
    (status,uid) = rfid.MFRC522_Anticoll()
    
    if status == rfid.MI_OK:
        print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
        
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag
        rfid.MFRC522_SelectTag(uid)

        # Authenticate
        status = rfid.MFRC522_Auth(rfid.PICC_AUTHENT1A, 8, key, uid)
        
        # Check if authenticated
        if status == rfid.MI_OK:
            data = rfid.MFRC522_Read(8)
            text = "".join(chr(x) for x in data)
            print(text)
            rfid.MFRC522_StopCrypto1()
        else:
            print("Authentication error")
            
        time.sleep(1)