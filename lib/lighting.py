from storage import PersistentDict
from leds import LEDs
from animation import Animation

colors = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "purple": (128, 0, 128),
}


class Lighting:
    def __init__(self):
        self.settings_object = PersistentDict()
        self.settings_object["lighting_settings"] = {
            "blink_1": {"target": 0, "function": "blink", "frequency": 2, "colors": ["white", "black"]},
            "blink_2": {"target": "1-3", "function": "blink", "frequency": 1, "colors": ["red", "blue"]},
            "pulse_1": {
                "target": 4,
                "function": "pulse",
                "frequency": 1.3,
                "duration": 1,
                "colors": ["white", "black"],
            },
            "fade_in_1": {
                "target": 5,
                "function": "fade_in",
                "duration": 120,
                "colors": ["red", "blue"],
            },
            "solid_1": {"function": "solid", "target": 6, "colors": ["purple"]},
        }
        self.settings = self.settings_object["lighting_settings"]
        self.leds = LEDs()
        self.animation = Animation(jobs={"lighting": self.process_tick}, stop_callbacks={"lighting": self.stop})

    def stop(self):
        """Runs on animation stop"""

        self.leds.clear()
        self.leds.show()

    def process_tick(self, tick_number: int):
        """Process a single tick of the lighting system."""

        for name, job in self.settings.items():
            if hasattr(self, job["function"]):
                func = getattr(self, job["function"])
                func(job, tick_number)

        self.leds.show()

    def get_color(self, input: str | tuple | list) -> tuple[int, int, int]:
        """Make sure that we have an RGB tuple"""

        if isinstance(input, str):
            return colors.get(input, (255, 255, 255))

        elif isinstance(input, list):
            return [self.get_color(color) for color in input]

        return colors

    def get_targets(self, target) -> list[int]:
        """Return a list of target indices for the given target specification."""

        if isinstance(target, int):
            return [target]

        elif isinstance(target, list):
            return target

        elif isinstance(target, str) and "-" in target:
            start, end = map(int, target.split("-"))
            return list(range(start, end + 1))

        return []

    def solid(self, job, tick):
        """Simple solid color function for a lighting job."""

        colors = self.get_color(job["colors"])
        targets = self.get_targets(job["target"])

        for target in targets:
            if self.leds.get(target) != colors[0]:
                self.leds.set(target, colors[0])

    def blink(self, job, tick):
        """Simple blink function for a lighting job."""

        interval = 40 // job.get("frequency", None)
        duration = interval
        colors = self.get_color(job["colors"])

        self.periodic(
            tick=tick, interval=interval, duration=duration, colors=colors, targets=self.get_targets(job["target"])
        )

    def pulse(self, job, tick):
        """Simple pulse function for a lighting job."""

        duration = job["duration"]
        interval = 40 // job.get("frequency", None) - duration
        colors = self.get_color(job["colors"])

        self.periodic(
            tick=tick, interval=interval, duration=duration, colors=colors, targets=self.get_targets(job["target"])
        )

    def periodic(self, tick, interval, duration, colors, targets):
        """blink function for a lighting job."""

        cycle_length = duration + interval
        phase = tick % cycle_length

        for target in targets:
            if phase < duration:
                self.leds.set(target, colors[0])
            else:
                self.leds.set(target, colors[1])

    def fade_in(self, job, tick):
        """Simple fade in function for a lighting job."""

        duration = job["duration"]
        colors = self.get_color(job["colors"])
        targets = self.get_targets(job["target"])

        phase = min(tick / duration, 1.0)
        r = int(colors[0][0] * (1 - phase) + colors[1][0] * phase)
        g = int(colors[0][1] * (1 - phase) + colors[1][1] * phase)
        b = int(colors[0][2] * (1 - phase) + colors[1][2] * phase)
        new_color = (r, g, b)

        for target in targets:
            if self.leds.get(target) != new_color:
                self.leds.set(target, new_color)
