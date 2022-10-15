# Code by Simon Monk https://github.com/simonmonk/

from multiprocessing.connection import Listener
import MFRC522
import RPi.GPIO as GPIO
import pygame
import sys

class SimpleMFRC522:

  READER = None;
  
  KEY = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
  BLOCK_ADDRS = [8, 9, 10]
  play_has_ended = False
  

  def __init__(self, screen):
    self.READER = MFRC522.MFRC522()
    self.screen = screen

  
  def read(self, playerVlc):
    id, text = self.read_no_block()
    while not id:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("escape pressed")
                sys.exit()
      if(playerVlc):
          self.check_status(playerVlc)
      id, text = self.read_no_block()
      print(id, text)
    return id, text

  def check_status(self, player):
    if(player):
      state = player.get_state()
      if self.is_playing(player) and self.play_has_ended:
        self.play_has_ended = False
      elif state == 6 and not self.play_has_ended:
        player.stop()
        self.screen.fill((0, 0, 0))
        pygame.display.update()
        self.play_has_ended = True

  def is_playing(self, player):
      playing = set([1,2,3,4])
      """ 
      VLC Status
          0: 'NothingSpecial'
          1: 'Opening'
          2: 'Buffering'
          3: 'Playing'
          4: 'Paused'
          5: 'Stopped'
          6: 'Ended'
          7: 'Error'
      """
      if(player):
        state = player.get_state()
        if state in playing:
          return True
        else:
          return False


  def read_id(self):
    id, text = self.read_no_block()        
    while not id:
      id, text = self.read_no_block()  
    return id

  def read_id_no_block(self):
    id, text = self.read_no_block()
    return id
  
  def read_no_block(self):
    (status, TagType) = self.READER.MFRC522_Request(self.READER.PICC_REQIDL)
    if status != self.READER.MI_OK:
        return None, None
    (status, uid) = self.READER.MFRC522_Anticoll()
    if status != self.READER.MI_OK:
        return None, None
    id = self.uid_to_num(uid)
    self.READER.MFRC522_SelectTag(uid)
    status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
    data = []
    text_read = ''
    if status == self.READER.MI_OK:
        for block_num in self.BLOCK_ADDRS:
            block = self.READER.MFRC522_Read(block_num) 
            if block:
            		data += block
        if data:
             text_read = ''.join(chr(i) for i in data)
    self.READER.MFRC522_StopCrypto1()
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
      status = self.READER.MFRC522_Auth(self.READER.PICC_AUTHENT1A, 11, self.KEY, uid)
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