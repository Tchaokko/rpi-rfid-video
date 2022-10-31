
import RPi.GPIO as GPIO
from MFRC522 import MFRC522
import re


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
                if(block_num == 5):
                    datachr += ''.join(chr(i) for i in block)
                    cleanedString = re.sub("[^\w.]+",'', datachr)
                else:
                    datachr += ''.join(chr(i) for i in block)
                    temp =  re.sub("[^\w.]+",'', datachr)
                    cleanedString += temp[-4:]
                block_num +=1

            self.MIFAREReader.MFRC522_StopCrypto1()
            return uid, cleanedString
        return None, None