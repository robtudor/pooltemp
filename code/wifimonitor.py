import os
import time
import urllib.request
import logging

wifi_name = 'wlan0'
enable_wifi = 'sudo ip link set "'+wifi_name+'" up'
disable_wifi = 'sudo ip link set "'+wifi_name+'" down'
logging.basicConfig(filename='/home/pi/Apps/wifimonitor.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

def connect():
    try:
        urllib.request.urlopen('http://google.com') #Python 3.x
        return True
    except:
        return False

logging.info('WiFi Monitor Started')

while True:
    if not connect():
#disable wifi, if network is OFFLINE
        logging.warning('Lost Access to Wifi')
        os.popen(disable_wifi)
        time.sleep(10)
#enable wifi
        os.popen(enable_wifi)
    time.sleep(20)
