# boot.py -- run on boot-up
import micropython

# set up the exception buffer so we can see what happens if we crash
micropython.alloc_emergency_exception_buf(100)

from utils.comms import WIFI

# Start the WIFI
WIFI()