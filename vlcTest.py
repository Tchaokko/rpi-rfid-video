# importing time and vlc
import time, vlc
import pygame, sys
import os

# method to play video
def video(source):
     
    # creating a vlc instance
    vlc_instance = vlc.Instance()
     
    
    # creating a media player
    player = vlc_instance.media_player_new()

    # creating a media
    media = vlc_instance.media_new(source)

    # setting media to the player
    player.set_media(media)
    
    # play the video
    player.play()
    player.toggle_fullscreen()
    time.sleep(0.5)
    # wait time
    timeout = time.time() + 5
    while True:
        if time.time() > timeout:
            break
    # getting the duration of the video
    duration = player.get_length()
     
    # printing the duration of the video
    print("Duration : " + str(duration))

# call the video method
#os.environ["DISPLAY"] = ":0"
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen.fill((0, 0, 0))
time.sleep(1)
video("/media/timestory3/76E8-CACF/rick.mkv")
