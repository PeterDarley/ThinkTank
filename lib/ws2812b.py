"""
Simple WS2812 (NeoPixel) helper for MicroPython.

Usage:
    from ws2812b import WS2812
    from machine import Pin

    strip = WS2812(pin=2, n=8, brightness=0.5)
    strip.fill((255,0,0))
    strip.show()

This wrapper provides convenience helpers and a global brightness scaler.
It intentionally keeps the API small and uses the builtin `neopixel.NeoPixel`.
"""

try:
    import neopixel
    from machine import Pin
except Exception:
    neopixel = None


class WS2812:
    def __init__(self, pin, n, brightness=1.0, pin_inverted=False):
        """Create a WS2812 controller.

        - pin: integer GPIO pin number or `machine.Pin` instance
        - n: number of LEDs
        - brightness: float 0.0-1.0 to scale colors (default 1.0)
        """
        if neopixel is None:
            raise RuntimeError('neopixel module not available')

        if isinstance(pin, int):
            pin = Pin(pin)

        self.n = int(n)
        self._np = neopixel.NeoPixel(pin, self.n)
        self._brightness = 1.0
        self.brightness = brightness

    def _scale(self, color):
        if self._brightness >= 0.999:
            return tuple(int(min(255, max(0, c))) for c in color)
        return tuple(int(min(255, max(0, int(c * self._brightness)))) for c in color)

    def set(self, i, color):
        """Set pixel `i` to `color` (r,g,b). Does not write to strip until `show()` is called."""
        if i < 0 or i >= self.n:
            return
        self._np[i] = self._scale(color)

    def get(self, i):
        """Return the raw value currently staged for pixel `i` (after brightness scaling)."""
        if i < 0 or i >= self.n:
            return (0, 0, 0)
        return tuple(self._np[i])

    def fill(self, color):
        """Fill the entire strip with `color` (r,g,b)."""
        scaled = self._scale(color)
        for i in range(self.n):
            self._np[i] = scaled

    def clear(self):
        """Clear the strip (set all pixels to off)."""
        self.fill((0, 0, 0))

    def show(self):
        """Push the currently staged colors to the LEDs."""
        try:
            self._np.write()
        except Exception:
            # some ports raise on consecutive writes in bad states; ignore
            pass

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, v):
        try:
            f = float(v)
        except Exception:
            f = 1.0
        if f < 0:
            f = 0.0
        if f > 1:
            f = 1.0
        self._brightness = f

    @staticmethod
    def wheel(pos):
        """Generate rainbow colors across 0-255."""
        pos = pos % 256
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)


# convenience factory
def WS(pin=2, n=8, brightness=1.0):
    return WS2812(pin, n, brightness)
