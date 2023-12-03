""" Package to facilitate communications. """
import settings

from network import WLAN, STA_IF
from machine import Pin, Timer

from utils.timing import TimerFactory

class WIFI:
    """ Singleton that manages the WIFI connection. """

    def __new__(cls, *args, **kwargs):
        """ Create a singleton. """

        if not hasattr(cls, "instance"):
            cls.instance: WIFI = super(WIFI, cls).__new__(cls)

        return cls.instance

    def __init__(self, *, ssid: str=None, password: str=None):
        """ Initialize the WIFI connection. """

        self.ssid: str = ssid or settings.WIFI["SSID"]
        self.password: str = password or settings.WIFI["PASSWORD"]

        self.sta_if: WLAN = WLAN(STA_IF)
        self.sta_if.active(True)
        
        if not self.ssid or not self.password:
            raise ValueError("SSID or password not provided.")

        self.sta_if.connect(self.ssid, self.password)
        if settings.WIFI["BLINK_ON_CONNECT"]:
            TimerFactory().get_timer(callback=self.check_connection_tick, periods=[1000], cycles=90)

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
            LED().blink(times=2)
            timer.stop(None)


class LED:
    """ Singleton that manages the LED. """

    def __new__(cls, *args, **kwargs):
        """ Create a singleton. """

        if not hasattr(cls, "instance"):
            cls.instance: LED = super(LED, cls).__new__(cls)

        return cls.instance

    def __init__(self, pin: int=None):
        """ Initialize the LED. """

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
        self.timer = TimerFactory().get_timer(callback=self.blink_tick, periods=[on_period, off_period], cycles=cycles, end_callback=self.blink_end)

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
        
        
