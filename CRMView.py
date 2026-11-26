"""
CRMView.py - Mini-Lab 4: IoT CRM Browser
Author: Emanuel Petrini

All output hardware: 16x2 LCD, 8-LED light ring, passive buzzer.
Light ring code for a customer:
  green = has activities, red = no activities yet, amber = details not loaded (option B).
"""

from Lights import GREEN, RED, BLUE, ORANGE, BLACK, PURPLE

NUM_LEDS = 8
WIDTH = 16


class CRMView:
    """Shows each screen of the CRM browser."""

    def __init__(self, lcd, strip, buzzer):
        """Receive the LCDDisplay, LightStrip, and PassiveBuzzer to drive."""
        self._lcd = lcd
        self._strip = strip
        self._buzzer = buzzer

    def show_mode_menu(self):
        """Start screen: choose loading option A or B."""
        self._write("CRM: pick mode", "Prev=A  Next=B")
        self._strip.setBrightness(0.2)
        for i in range(NUM_LEDS):
            self._strip.setPixel(i, BLUE if i < NUM_LEDS // 2 else PURPLE, show=False)
        self._strip.show()

    def show_progress(self, text, done, total):
        """Loading screen with a progress bar on the light ring."""
        self._write(text, f"{done}/{total}")
        lit = (done * NUM_LEDS) // total if total else 0
        self._strip.setBrightness(0.2)
        self._strip.setColor(BLUE, lit)

    def show_ready(self, mode, count, seconds, requests):
        """Summary after loading: how many customers, how long, how many REST calls."""
        self._write(f"Mode {mode}: {count} cust", f"{seconds:.1f}s {requests} calls")
        self._buzzer.beep(880, 80)
        self._buzzer.beep(1320, 120)

    def show_error(self, line2):
        """Network or web service failure."""
        self._write("Network error", line2)
        self._strip.setBrightness(0.3)
        self._strip.setColor(RED)
        self._buzzer.beep(200, 400)

    def show_customer(self, customer, index, total):
        """Customer browsing screen, colour-coded on the light ring."""
        if customer.details_loaded:
            info = f"{len(customer.contacts)}c {len(customer.activities)}a"
        else:
            info = "tap Select"
        self._write(customer.name, f"{index + 1}/{total} {info}")
        self._strip.setBrightness(0.2)
        if not customer.details_loaded:
            self._strip.setColor(ORANGE)
        elif customer.has_activities():
            self._strip.setColor(GREEN)
        else:
            self._strip.setColor(RED)
        self._buzzer.beep(1000, 30)

    def show_contact(self, customer, contact, index, total):
        """One contact of the selected customer (or a 'no contacts' screen)."""
        if contact is None:
            self._write("No contacts", customer.name)
            self._buzzer.beep(300, 150)
            return
        self._write(contact.name, f"{index + 1}/{total} {contact.title}")
        self._buzzer.beep(1200, 30)

    def show_activity(self, customer, activity, index, total):
        """One activity of the selected customer (or a 'no activities' screen)."""
        if activity is None:
            self._write("No activities", customer.name)
            self._strip.setColor(RED)
            self._buzzer.beep(300, 150)
            return
        self._write(activity.name, f"{activity.short_date()} {activity.activity_type}")
        self._strip.setColor(GREEN)
        self._buzzer.beep(1400, 30)

    def _write(self, line1, line2):
        """Write two lines to the LCD, padded or cut to exactly 16 characters."""
        self._lcd.showText((str(line1) + " " * WIDTH)[:WIDTH], 0)
        self._lcd.showText((str(line2) + " " * WIDTH)[:WIDTH], 1)
