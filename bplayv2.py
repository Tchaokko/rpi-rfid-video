#!/usr/bin/python3
from random import randint
from SimpleMFRC522 import SimpleMFRC522
import vlc
from pathlib import Path
import time
import os
import logging
import random
import glob
import RPi.GPIO as GPIO
import pygame
from cec import CustomCec
import json
import sys


class MainClass:
	playerVLC = vlc.MediaPlayer()
	reader = ''
	play_has_ended = False
	videoPath = ''

	def __init__(self):
		self.screen = self.activate_blackscreen()
		file = open('config.json')
		data = json.load(file)
		self.videoPath = data['usbPath']
		self.reader = SimpleMFRC522()
		pass

	def playmovie(self,video,directory):

		"""plays a video."""
		cec = CustomCec()
		VIDEO_PATH = Path(directory + video)

		isPlay = self.is_playing()

		if not isPlay:

			logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + 'playmovie: No videos playing, so play video.')

		else:

			logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+ 'playmovie: Video already playing, so quit current video, then play')
			self.playerVLC.stop()
		try:
			cec.force_hdmi_to_input()
			time.sleep(2)
			win_id = pygame.display.get_wm_info()['window']
			self.playerVLC.set_xwindow(win_id)
			media = vlc.Media(VIDEO_PATH)
			pygame.mouse.set_visible(False)
			self.playerVLC.set_media(media)
			self.playerVLC.play()
		except SystemError:
			logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' $Error: Cannot Find Video.')

		logging.info('playmovie: vlc %s' % video)

		time.sleep(2)

	def quit_player_if_ended(self):
		print('quit_player_if_ended')
		if(self.playerVLC):
			state = self.playerVLC.get_state()
			print(state)	
			if state == 6:
				self.playerVLC.exit()


	def activate_blackscreen(self):
		pygame.init()
		pygame.mouse.set_visible(False)
		screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
		screen.fill((0, 0, 0))
		return screen

	def stop_player_if_video_ended(self):
		state = self.playerVLC.get_state()
		if self.is_playing() and self.play_has_ended:
			self.play_has_ended = False
		elif state == 6 and not self.play_has_ended:
			self.playerVLC.stop()
			self.screen.fill((0, 0, 0))
			pygame.display.update()
			self.play_has_ended = True

	def is_playing(self):
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
		if(self.playerVLC):
			state = self.playerVLC.get_state()
			if state in playing:
				return True
			else:
				return False

	def main_loop(self):

	
		# toggling full screen
		
		# playerVLC.toggle_fullscreen()
		LOG_FILENAME = '/tmp/bplay_%s.log' %time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).replace(" ","_").replace(":","")
		logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
		#logging.basicConfig(level=logging.DEBUG)
		logging.info("\n\n\n***** %s Begin Player****\n\n\n" %time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
		current_movie_id = 111111222222


		while True:
			try:

				isPlay = self.is_playing()
				#quit_player_if_ended(playerVLC)

				logging.debug(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " Movie Playing: %s" % isPlay)

				if not isPlay:
					current_movie_id = 555555555555
					
				start_time = time.time()
				logging.debug('start_time0: %s' %start_time)

				logging.debug(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " Waiting for ID to be scanned")
				
				temp_time = time.time()
				logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " #READER BEFORE %s" %temp_time)
				idd, movie_name = self.reader.read()
				while not idd:
					idd, movie_name = self.reader.read()
					for event in pygame.event.get():
						if event.type == pygame.QUIT:
							sys.exit()
						if event.type == pygame.KEYDOWN:
							if event.key == pygame.K_ESCAPE:
								print("escape pressed")
								sys.exit()
					if(self.playerVLC):
						self.stop_player_if_video_ended()

				temp_time = time.time() - temp_time
				logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " #READER AFTER - ELAPSED TIME %s" %temp_time)

				logging.debug(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " + ID: %s" % idd)
				logging.debug(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " + Movie Name: %s" % movie_name)

				movie_name = movie_name.rstrip()

				if current_movie_id != idd:

					logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' New Movie')
					logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " - ID: %s" % idd)
					logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " - Name: %s" % movie_name)
					#this is a check in place to prevent omxplayer from restarting video if ID is left over the reader.
					#better to use id than movie_name as there can be a problem reading movie_name occasionally
					

					if movie_name.endswith(('.mp4', '.avi', '.m4v','.mkv')):
						current_movie_id = idd 	#we set this here instead of above bc it may mess up on first read
						logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " playing: omxplayer %s" % movie_name)
						
					self.playmovie(movie_name,self.videoPath)
			except KeyboardInterrupt:
				print('exit')
				GPIO.cleanup()
				print("\nAll Done")

if __name__ == '__main__':
	
	os.environ["DISPLAY"] = ":0"
	mainclass = MainClass()
	mainclass.main_loop()
	

