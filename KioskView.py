"""
KioskView.py - Mini-Lab 3: Satisfaction Kiosk
Author: Emanuel Petrini

View class: owns every piece of output hardware (16x2 LCD, 8-LED light
strip, passive buzzer). The controller never talks to the hardware directly.
"""

from Lights import GREEN, RED, BLUE, ORANGE, BLACK

NUM_LEDS = 8
LCD_WIDTH = 16


class KioskView:
    """
    Shows each kiosk screen on the LCD, light strip, and buzzer.
    One public method per screen, plus the non-blocking siren used in ALARM.
    """

    def __init__(self, lcd, strip, buzzer):
        """Receive the LCDDisplay, LightStrip, and PassiveBuzzer to drive."""
        self._lcd = lcd
        self._strip = strip
        self._buzzer = buzzer
        self._siren_high = False

    def show_idle(self, pct, total):
        """Idle screen: invite customers and show the satisfaction gauge."""
        if total == 0:
            self._write("Step closer :)", "No votes yet")
        else:
            self._write("Rate your visit", f"{pct}% happy n={total}")
        self._show_gauge(pct, total)

    def show_prompt(self):
        """Ask for a vote: left half of the strip green, right half red."""
        self._write("Rate your visit!", "Green=:) Red=:(")
        self._strip.setBrightness(0.4)
        for i in range(NUM_LEDS):
            self._strip.setPixel(i, GREEN if i < NUM_LEDS // 2 else RED, show=False)
        self._strip.show()

    def show_thanks(self, positive, pct, total):
        """Thank the customer, show the new score, and beep high or low."""
        self._write("Thanks! :)" if positive else "Sorry! :(", f"{pct}% happy n={total}")
        self._strip.setBrightness(0.4)
        self._strip.setColor(GREEN if positive else RED)
        self._buzzer.beep(1200 if positive else 300, 150)

    def show_alarm(self, pct):
        """Low-satisfaction alert for the manager."""
        self._write(f"LOW SCORE {pct}%", "Call manager!")
        self._siren_high = False

    def siren_step(self):
        """
        One non-blocking step of the siren: alternate two tones and flash the
        strip red/off. Called repeatedly from the ALARM do-activity.
        """
        self._siren_high = not self._siren_high
        self._buzzer.play(880 if self._siren_high else 620)
        self._strip.setBrightness(0.6)
        self._strip.setColor(RED if self._siren_high else BLACK)

    def silence(self):
        """Stop the siren and turn the strip off."""
        self._buzzer.stop()
        self._strip.setColor(BLACK)

    def show_manager_menu(self, pct, total):
        """Manager screen: current score and button options."""
        self._write(f"Score {pct}% n={total}", "Grn=done Red=rst")
        self._strip.setBrightness(0.2)
        self._strip.setColor(ORANGE)

    def show_reset(self):
        """Confirm that the manager reset the statistics."""
        self._write("Stats reset", "Grn=done")
        self._strip.setBrightness(0.1)
        self._strip.setColor(BLUE)
        self._buzzer.beep(600, 100)

    def _show_gauge(self, pct, total):
        """Satisfaction gauge: green share of LEDs = positive share; dim blue if no votes."""
        self._strip.setBrightness(0.1)
        if total == 0:
            self._strip.setColor(BLUE)
            return
        green = round(pct * NUM_LEDS / 100)
        for i in range(NUM_LEDS):
            self._strip.setPixel(i, GREEN if i < green else RED, show=False)
        self._strip.show()

    def _write(self, line1, line2):
        """Write two lines to the LCD, padded or cut to exactly 16 characters."""
        self._lcd.showText((line1 + " " * LCD_WIDTH)[:LCD_WIDTH], 0)
        self._lcd.showText((line2 + " " * LCD_WIDTH)[:LCD_WIDTH], 1)
