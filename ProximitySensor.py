"""
ProximitySensor.py - Mini-Lab 3: Satisfaction Kiosk
Author: Emanuel Petrini

A safer version of PicoLibrary's UltrasonicSensor for detecting a customer.
"""

from Sensors_advanced import UltrasonicSensor


class ProximitySensor(UltrasonicSensor):
    """
    HC-SR04 proximity sensor that reports "tripped" when someone is closer
    than the threshold distance.

    PicoLibrary's UltrasonicSensor.distance() returns -1 when a reading fails,
    and the original tripped() treats -1 as "closer than the threshold". This
    subclass ignores failed readings so the kiosk never wakes up on its own.
    """

    def __init__(self, *, trigger, echo, name, threshold):
        """Create the sensor on the given trigger and echo pins (keyword-only)."""
        super().__init__(trigger=trigger, echo=echo, name=name,
                         lowActive=True, threshold=threshold)

    def tripped(self):
        """Return True only for a valid reading closer than the threshold (in cm)."""
        distance = self.distance()
        return 0 <= distance < self._threshold
