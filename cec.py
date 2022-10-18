import subprocess
import sys

class CustomCec:

    def __init__(self) -> None:
        pass

    def turn_on_tv(self):
        process = subprocess.Popen("echo 'on 0' | cec-client RPI -s -d 1", stdout=subprocess.PIPE, shell=True)
        process.communicate()
    
    def force_hdmi_to_other_input(self):
        process = subprocess.Popen("echo "is" | cec-client RPI -s -d 1", stdout=subprocess.PIPE, shell=True)
        process.communicate()

    def turn_off_tv(self):
        pass
    def force_hdmi_to_input(self):
        process = subprocess.Popen("echo 'as' | cec-client -s -d 1", stdout=subprocess.PIPE, shell=True)
        process.communicate()

    def scan_client(self):
        process = subprocess.Popen("echo 'scan' | cec-client -s -d 1", stdout=subprocess.PIPE, shell=True)
        process.communicate()