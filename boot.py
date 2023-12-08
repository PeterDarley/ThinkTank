# boot.py -- run on boot-up
import micropython              # type: ignore

# set up the exception buffer so we can see what happens if we crash
micropython.alloc_emergency_exception_buf(100)

from utils.comms import WIFI, IIC

# Start the WIFI
WIFI()

# Start the I2C
IIC()