import constants
import time
from network import WLAN, STA_IF

def connect():    
    wlan = WLAN(STA_IF)
    wlan.active(True)
    time.sleep(1)
    wlan.connect(constants.SSID, constants.PASSWORD)
    while not wlan.isconnected():
        print("Connecting...")
        time.sleep(1)