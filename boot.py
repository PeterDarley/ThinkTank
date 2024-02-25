# boot.py -- run on boot-up

import machine                  # type: ignore
import micropython              # type: ignore

import settings


# set up the exception buffer so we can see what happens if we crash
micropython.alloc_emergency_exception_buf(100)

from comms import WIFIManager, I2CManager     # type: ignore

print("\nBooting...")

# Set the CPU frequency
if hasattr(settings, "BOARD") and "CPU_Frequency" in settings.BOARD:
    machine.freq(settings.BOARD["CPU_Frequency"])

# Start the WIFI
WIFIManager()

# Start the I2C
I2CManager()

print("Boot complete.\n")