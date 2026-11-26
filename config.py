"""
config.py - Mini-Lab 4: IoT CRM Browser
Author: Emanuel Petrini

Settings for the WiFi network and the CRM web service.
On Wokwi use the simulator's open network "Wokwi-GUEST" with no password.
On the real Pico 2 W, put your phone hotspot name and password here.
"""

WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = None          # None = open network; use a string for a hotspot

BASE_URL = "https://iacademy.oracle.com/ords/ism6106/customer/"

# Name of the customer I added to the CRM (TODO 1). The kiosk starts on it.
MY_CUSTOMER = "Emanuel Petrini"
