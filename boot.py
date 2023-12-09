# boot.py -- run on boot-up
import micropython              # type: ignore

# set up the exception buffer so we can see what happens if we crash
micropython.alloc_emergency_exception_buf(100)

from comms import WIFIManager, I2CManager     # type: ignore

print("\nBooting...")

# Start the WIFI
WIFIManager()

# Start the I2C
I2CManager()

print("Boot complete.\n")