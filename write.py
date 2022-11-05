#!/usr/bin/env python

import RPi.GPIO as GPIO
import SimpleMFRC522
from MFRC522 import MFRC522
reader = SimpleMFRC522.SimpleMFRC522()
readerUpdated = MFRC522()
print('Scan Card')

try:

    while True:

        text = ('toto.mkv')

        # if len(text) > 48:

        #     text = raw_input('Data was too long, shorten it and type it here:')

        print("Now place your tag to write")
        
        reader.write(text)
        print("Written")


except KeyboardInterrupt:
        GPIO.cleanup()
        print("\nClean Exit")
