
import RPi.GPIO as GPIO
from MFRC522UPDATED import MFRC522
import re

continue_reading = True


class UltralightRead:

    def __init__(self):
        self.MIFAREReader = MFRC522()
        pass

    def read(self):  
        # Scan for cards    
        (status,TagType) = self.MIFAREReader.MFRC522_Request(self.MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == self.MIFAREReader.MI_OK:
            print ("Card detected")
        
        # Get the UID of the card
        (status,uid) = self.MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == self.MIFAREReader.MI_OK:

            # Print UID
            print ("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
        
            # This is the default key for authentication
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
            
            # Select the scanned tag
            self.MIFAREReader.MFRC522_SelectTag(uid)

            block_num = 5
            while block_num < 8:
                block = self.MIFAREReader.MFRC522_Read(block_num) 
                datachr = ''
                result = ''
                if(block_num == 5):
                    datachr += ''.join(chr(i) for i in block)
                    cleanedString = re.sub("[^\w.]+",'', datachr)
                    # cleanedString = ''.join(e for e in datachr if e.isalnum())
                else:
                    datachr += ''.join(chr(i) for i in block)
                    # temp = ''.join(e for e in datachr if e.isalnum())
                    temp =  re.sub("[^\w.]+",'', datachr)
                    cleanedString += temp[-4:]
                block_num +=1

            print(cleanedString)
            self.MIFAREReader.MFRC522_StopCrypto1()
            return uid, cleanedString
        return None, None


# Create an object of the class MFRC522

# Welcome message
print ("Welcome to the MFRC522 data read example")
print ("Press Ctrl-C to stop.")

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
