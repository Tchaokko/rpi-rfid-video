# Code by Simon Monk https://github.com/simonmonk/

from multiprocessing.connection import Listener
from MFRC522UPDATED import MFRC522
import RPi.GPIO as GPIO
import pygame
import sys

class SimpleMFRC522:

  READER = None;
  
  KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
  BLOCK_ADDRS_ULTRALIGHT = [256, 257, 258]
  BLOCK_ADDRS = [8, 9, 10]
  

  def __init__(self):
    self.READER = MFRC522()

  
  def read(self):
    id, text = self.read_no_block()
    return id, text

  def read_id(self):
    id, text = self.read_no_block()        
    while not id:
      id, text = self.read_no_block()  
    return id

  def read_id_no_block(self):
    id, text = self.read_no_block()
    return id, text
  
  def read_no_block(self):
    (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
    if status != self.READER.MI_OK:
        return None, None
    (status, uid) = self.READER.MFRC522_Anticoll()
    if status != self.READER.MI_OK:
        return None, None
    id = self.uid_to_num(uid)
    self.READER.MFRC522_SelectTag(uid)
#    status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1B, 11, self.KEY, uid)
    data = []
    text_read = ''
    if status == self.READER.MI_OK:
      block_num = 4
      while block_num < 16:
        block = self.READER.MFRC522_Read(block_num) 
        block_num +=1
        if block:
            data += block
      if data:
            text_read = ''.join(chr(i) for i in data)
    self.READER.MFRC522_StopCrypto1()
    return id, text_read
  
  def ultralight_read(self):
      # Scan for cards    
    (status,TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
    if status != self.READER.MI_OK:
        return None, None
    # If a card is found
    if status == self.READER.MI_OK:
        print("Card detected")
    
    # Get the UID of the card
    (status,uid) = self.READER.MFRC522_Anticoll()
    if status != self.READER.MI_OK:
        return None, None
    # If we have the UID, continue

    # Print UID
    print("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
    id = self.uid_to_num(uid)
    
    # Select the scanned tag
    self.READER.MFRC522_SelectTag(uid)

    data = []
    if status == self.READER.MI_OK:
      for block_num in self.BLOCK_ADDRS_ULTRALIGHT:
        block = self.READER.MFRC522_Read(block_num)
        if block:
            data += block
      if data:
          text_read = ''.join(chr(i) for i in data)
      self.READER.MFRC522_StopCrypto1()
    else:
        print("Authentication error")
    return id, text_read
    
  def write(self, text):
      id, text_in = self.write_no_block(text)        
      while not id:
          id, text_in = self.write_no_block(text)  
      return id, text_in


  def write_no_block(self, text):
      (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
      if status != self.READER.MI_OK:
          return None, None
      (status, uid) = self.READER.MFRC522_Anticoll()
      if status != self.READER.MI_OK:
          return None, None
      id = self.uid_to_num(uid)
      self.READER.MFRC522_SelectTag(uid)
     # status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
      self.READER.MFRC522_Read(11)
      if status == self.READER.MI_OK:
          data = bytearray()
          data.extend(bytearray(text.ljust(len(self.BLOCK_ADDRS) * 16).encode('ascii')))
          i = 0
          for block_num in self.BLOCK_ADDRS:
            self.READER.MFRC522_Write(block_num, data[(i*16):(i+1)*16])
            i += 1
      self.READER.MFRC522_StopCrypto1()
      return id, text[0:(len(self.BLOCK_ADDRS) * 16)]
      
  def uid_to_num(self, uid):
      n = 0
      for i in range(0, 5):
          n = n * 256 + uid[i]
      return n