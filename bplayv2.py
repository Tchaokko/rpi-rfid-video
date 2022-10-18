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

def playmovie(video,directory,player, reader):

	"""plays a video."""
	cec = CustomCec()
	VIDEO_PATH = Path(directory + video)

	isPlay = reader.is_playing(player)

	if not isPlay:

		logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + 'playmovie: No videos playing, so play video.')

	else:

		logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))+ 'playmovie: Video already playing, so quit current video, then play')
		player.stop()
	try:
		cec.force_hdmi_to_input()
		time.sleep(2)
		win_id = pygame.display.get_wm_info()['window']
		player.set_xwindow(win_id)
		media = vlc.Media(VIDEO_PATH)
		pygame.mouse.set_visible(False)
		player.set_media(media)
		player.play()
	except SystemError:
		logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ' $Error: Cannot Find Video.')

	logging.info('playmovie: vlc %s' % video)

	time.sleep(2)

	return player

def quit_player_if_ended(player):
	print('quit_player_if_ended')
	if(player):
		state = player.get_state()
		print(state)	
		if state == 6:
			player.exit()


def activate_blackscreen():
	pygame.init()
	pygame.mouse.set_visible(False)
	screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
	screen.fill((0, 0, 0))
	return screen

def main():

	screen = activate_blackscreen()

	#program start
	playerVLC = vlc.MediaPlayer()
 
	# toggling full screen
	
	# playerVLC.toggle_fullscreen()
	directory = '/media/timestory3/76E8-CACF/'

	LOG_FILENAME = '/tmp/bplay_%s.log' %time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())).replace(" ","_").replace(":","")
	logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
	#logging.basicConfig(level=logging.DEBUG)

	reader = SimpleMFRC522(screen)

	logging.info("\n\n\n***** %s Begin Player****\n\n\n" %time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

	current_movie_id = 111111222222

	#playerVLC = ""

	while True:
		try:

			isPlay = reader.is_playing(playerVLC)
			#quit_player_if_ended(playerVLC)

			logging.debug(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " Movie Playing: %s" % isPlay)

			if not isPlay:
				current_movie_id = 555555555555
				
			start_time = time.time()
			logging.debug('start_time0: %s' %start_time)

			logging.debug(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " Waiting for ID to be scanned")
			
			temp_time = time.time()
			logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " #READER BEFORE %s" %temp_time)
			idd, movie_name = reader.read(playerVLC)

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
					
					playerVLC = playmovie(movie_name,directory,playerVLC,reader)
					

				elif 'folder' in movie_name:
					current_movie_id = idd
					movie_directory = movie_name.replace('folder',"") 
					
					try:

						movie_name = random.choice(glob.glob(os.path.join(directory + movie_directory, '*')))
						movie_name = movie_name.replace(directory,"")
						direc = directory
					except IndexError:
						movie_name = 'videonotfound.mp4'
						direc = 'home/pi/Videos/'

					logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + " randomly selected: omxplayer %s" % movie_name)
					playerVLC = playmovie(movie_name,direc,playerVLC)

		except KeyboardInterrupt:
			print('exit')
			GPIO.cleanup()
			print("\nAll Done")

if __name__ == '__main__':
	os.environ["DISPLAY"] = ":0"
	main()

