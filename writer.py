#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal

name=input("Please enter the name for the card: ")
if len(name)>16:
    name=name[:16]
data = [ord(x) for x in list(name)]

rfid = MFRC522.MFRC522()

reading = True
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
        
        if status == rfid.MI_OK:
            for x in range(0,16):
                data.append(0x00)

            print("The original data was:")
            # Read block 8
            rfid.MFRC522_Read(8)

            rfid.MFRC522_Write(8, data)
            
            print("Now the data is:")
            # Check to see if it was written
            rfid.MFRC522_Read(8)

            # Stop
            rfid.MFRC522_StopCrypto1()

            # Make sure to stop reading for cards
            reading = False
        else:
            print("Authentication error")