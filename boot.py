# boot.py -- run on boot-up

import machine                  # type: ignore
import micropython              # type: ignore

import settings

# set up the exception buffer so we can see what happens if we crash
micropython.alloc_emergency_exception_buf(100)

from comms import WIFIManager, I2CManager     # type: ignore
from webserver import WebServer  # type: ignore

print("\nBooting...")

# Set the CPU frequency
if hasattr(settings, "BOARD") and "CPU_Frequency" in settings.BOARD:
    machine.freq(settings.BOARD["CPU_Frequency"])

# Create the web server
web_server = WebServer(port=80, debug=True)

# Start the WIFI
WIFIManager(callback=web_server.start_in_thread)

# Start the I2C
# I2CManager()

print("Boot complete.\n")