""" Package to facilitate communications. """

import settings
from collections import OrderedDict

from machine import Pin, Timer, I2C             # type: ignore
from network import WLAN, STA_IF                # type: ignore
from time import time_ns    
from ustruct import pack                        # type: ignore

from timing import TimerManager
from utils import bytes_to_int

class WIFIManager:
    """ Singleton that manages the WIFI connection. """

    def __new__(cls, *args, **kwargs):
        """ Create a singleton. """

        if not hasattr(cls, "instance"):
            cls.instance: WIFIManager = super(WIFIManager, cls).__new__(cls)

        return cls.instance

    def __init__(self, *, ssid: str=None, password: str=None):
        """ Initialize the WIFI connection. """

        if not hasattr(self, "sta_if"):
            self.ssid: str = ssid or settings.WIFI["SSID"]
            self.password: str = password or settings.WIFI["Password"]

            self.sta_if: WLAN = WLAN(STA_IF)
            self.sta_if.active(True)
            
            if not self.ssid or not self.password:
                raise ValueError("SSID or password not provided.")

            self.sta_if.connect(self.ssid, self.password)
            
            if settings.WIFI.get("Blink_on_connect"):
                TimerManager().get_timer(callback=self.check_connection_tick, periods=[1000], cycles=90)

            if settings.WIFI.get("Print_on_connect"):
                print(self)

    @property
    def is_connected(self):
        """ Check if the WIFI is connected. """

        return self.sta_if.isconnected()

    @property 
    def ip(self):
        """ Return the IP address. """

        return self.sta_if.ifconfig()[0]

    def __str__(self):
        """ Return the WIFI status. """

        return f"IP: {self.ip}, Connected: {self.is_connected}"
    
    def check_connection_tick(self, timer):
        """ Check the WIFI connection repeatedly until it's up, or our counter reaches zero. """

        if self.is_connected:
            LEDManager().blink(times=2)
            timer.stop(None)


class LEDManager:
    """ Singleton that manages the LED. """

    def __new__(cls, *args, **kwargs):
        """ Create a singleton. """

        if not hasattr(cls, "instance"):
            cls.instance: LEDManager = super(LEDManager, cls).__new__(cls)

        return cls.instance

    def __init__(self, pin: int=None):
        """ Initialize the LED. """

        if not hasattr(self, "led"):
            self.led: Pin = Pin(pin or settings.PINS["LED"], Pin.OUT)
            self.blinking: bool = False
            self.blink_count: int = 0
            self.timer: Timer = None

    def __str__(self):
        """ Return the LED status. """

        return f"LED is {'on' if self.led.value() else 'off'}"

    @property
    def value(self):
        """ Return the LED value. """

        return self.led.value()

    def on(self):
        """ Turn the LED on. """

        self.led.on()

    def off(self):
        """ Turn the LED off. """

        self.led.off()

    def toggle(self):
        """ Toggle the LED. """

        self.led.value(not self.led.value())
    
    def blink(self, *, times: int=5, on_period: int=250, off_period: int=125):
        """ Blink the LED. """

        cycles = times * 2 - 1

        if self.blinking: 
            return False
        
        self.blinking = True
        self.timer = TimerManager().get_timer(callback=self.blink_tick, periods=[on_period, off_period], cycles=cycles, end_callback=self.blink_end)

        return True

    def blink_tick(self, _):
        """ Blink the LED. """

        self.toggle()
    
    def blink_end(self, _):
        """ End the blinking. """

        self.blinking = False
        self.timer = None

    def blink_stop(self):
        """ Stop the blinking. """
        
        self.off()

        if self.timer:
            self.timer.stop()
        

class I2CManager:
    """ Singleton that manages the I2C bus. """

    def __new__(cls, *args, **kwargs):
        """ Create a singleton. """

        if not hasattr(cls, "instance"):
            cls.instance: I2CManager = super(I2CManager, cls).__new__(cls)

        return cls.instance
    
    def __init__(self) -> None:
        """ Initialize the I2C bus. """
        
        if not hasattr(self, "i2c"):
            self.i2c: I2C = I2C(0, scl=Pin(settings.PINS["SCL"]), sda=Pin(settings.PINS["SDA"]), freq=settings.I2C["Freq"])
            
            self.devices: dict = {}
            self.scan: list = self.i2c.scan()

            for id, device in settings.I2C["IDs"].items():
                if id in self.scan:
                    if device == "AccelGyro":
                        self.devices[device] = self.AccelGyro(name=device, address=id)
                    if device == "Compass":
                        self.devices[device] = self.Compass(name=device, address=id)
                    else:
                        self.devices[device] = self.Device(name=device, address=id)

            if settings.I2C.get("Blink_on_connect"):
                LEDManager().blink(times=3)

            if settings.I2C.get("Print_on_connect"):
                print(self)
                
    class Device:
        """ Device on the I2C bus. """

        def __init__(self, name: str, address: int) -> None:
            """ Initialize the device. """

            self.name: str = name
            self.address: int = address
            self.i2c = I2CManager().i2c

    class AccelGyro(Device):
        """ Accelerometer/Gyroscope. 
        Based on https://github.com/adamjezek98/MPU6050-ESP8266-MicroPython, with thanks."""

        def __init__(self, name: str, address: int) -> None:
            """ Initialize the device. """

            super().__init__(name=name, address=address)

            self.i2c.writeto(self.address, bytearray([107, 0]))

            self.values: OrderedDict[str: int] = OrderedDict([
                ("time_ns", None),
                ("accel_x", None),
                ("accel_y", None),
                ("accel_z", None),
                ("gyro_x", None),
                ("gyro_y", None),
                ("gyro_z", None),
                ("temp", None),
            ])

        def get_values(self) -> OrderedDict[str: int]:
            """ Load and return the raw values. """

            bytes: bytearray = self.i2c.readfrom_mem(self.address, 0x3B, 14)
            self.values["time_ns"] = time_ns()
            self.values["accel_x"] = bytes_to_int(bytes[0], bytes[1])
            self.values["accel_y"] = bytes_to_int(bytes[2], bytes[3])
            self.values["accel_z"] = bytes_to_int(bytes[4], bytes[5])
            self.values["temp"] = bytes_to_int(bytes[6], bytes[7]) / 340.00 + 36.53
            self.values["gyro_x"] = bytes_to_int(bytes[8], bytes[9]) / settings.GYRO["Scale_factor"]
            self.values["gyro_y"] = bytes_to_int(bytes[10], bytes[11]) / settings.GYRO["Scale_factor"]
            self.values["gyro_z"] = bytes_to_int(bytes[12], bytes[13]) / settings.GYRO["Scale_factor"]

            return self.values

    class Compass(Device):
        """ Compass. 
        Based on https://github.com/gvalkov/micropython-esp8266-hmc5883l/blob/master/hmc5883l.py, with thanks."""

        __gain__ = {
            '0.88': (0 << 5, 0.73),
            '1.3':  (1 << 5, 0.92),
            '1.9':  (2 << 5, 1.22),
            '2.5':  (3 << 5, 1.52),
            '4.0':  (4 << 5, 2.27),
            '4.7':  (5 << 5, 2.56),
            '5.6':  (6 << 5, 3.03),
            '8.1':  (7 << 5, 4.35)
        }

        def __init__(self, name: str, address: int, gauss: str="1.3") -> None:
            """ Initialize the device. 
            Don't know how the gauss is determined, but it's the default in the Arduino library."""

            super().__init__(name=name, address=address)

            # Configuration register A:
            #   0bx11xxxxx  -> 8 samples averaged per measurement
            #   0bxxx100xx  -> 15 Hz, rate at which data is written to output registers
            #   0bxxxxxx00  -> Normal measurement mode
            self.i2c.writeto_mem(self.address, 0x00, pack('B', 0b111000))

            # Configuration register B:
            reg_value, self.gain = self.__gain__[gauss]
            self.i2c.writeto_mem(self.address, 0x01, pack('B', reg_value))

            # Set mode register to continuous mode.
            self.i2c.writeto_mem(self.address, 0x02, pack('B', 0x00))

            self.values: OrderedDict[str: int] = OrderedDict([
                ("time_ns", None),
                ("compass_x", None),
                ("compass_y", None),
                ("compass_z", None),
            ])

        def get_values(self) -> OrderedDict[str: int]:
            """ Load and return the raw values. """

            bytes: bytearray = self.i2c.readfrom_mem(self.address, 0x03, 6)
            # self.values["time_ns"] = time_ns()
            # self.values["compass_x"] = bytes_to_int(bytes[0], bytes[1])
            # self.values["compass_y"] = bytes_to_int(bytes[4], bytes[5])
            # self.values["compass_z"] = bytes_to_int(bytes[2], bytes[3])

            # return self.values
            return bytes
        
    def __str__(self):
        """ Return the I2C status. """
        
        return f"I2C devices: " + ", ".join([f"{device.name} at {device.address}" for device in self.devices.values()])