""" Constants for the QMC5883L magnetometer. 
From https://github.com/robert-hh/QMC5883, with thanks. """

from micropython import const        # type: ignore

try:
    _canary = const(0xfeed)
except:
    const = lambda x: x

# Default I2C address
ADDR = const(0x0D) 

# QMC5883 Register numbers
X_LSB = const(0)
X_MSB = const(1)
Y_LSB = const(2)
Y_MSB = const(3)
Z_LSB = const(4)
Z_MSB = const(5)
STATUS = const(6)
T_LSB = const(7)
T_MSB = const(8)
CONFIG = const(9)
CONFIG2 = const(10)
RESET = const(11)
STATUS2 = const(12)
CHIP_ID = const(13)

# Bit values for the STATUS register
STATUS_DRDY = const(1)
STATUS_OVL = const(2)
STATUS_DOR = const(4)

# Oversampling values for the CONFIG register
CONFIG_OS512 = const(0b00000000)
CONFIG_OS256 = const(0b01000000)
CONFIG_OS128 = const(0b10000000)
CONFIG_OS64 = const(0b11000000)

# Range values for the CONFIG register
CONFIG_2GAUSS = const(0b00000000)
CONFIG_8GAUSS = const(0b00010000)

# Rate values for the CONFIG register
CONFIG_10HZ = const(0b00000000)
CONFIG_50HZ = const(0b00000100)
CONFIG_100HZ = const(0b00001000)
CONFIG_200HZ = const(0b00001100)

# Mode values for the CONFIG register
CONFIG_STANDBY = const(0b00000000)
CONFIG_CONT = const(0b00000001)

# Mode values for the CONFIG2 register
CONFIG2_INT_DISABLE = const(0b00000001)
CONFIG2_ROL_PTR = const(0b01000000)
CONFIG2_SOFT_RST = const(0b10000000)