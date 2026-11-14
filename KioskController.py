"""
KioskController.py - Mini-Lab 3: Satisfaction Kiosk
Author: Emanuel Petrini

Controller and StateModel handler for the kiosk, following the structure of
PicoLibrary's ModelTemplate.py. Implements the revised state diagram:

    IDLE (0) --proximity_trip--> PROMPT (1)
    IDLE (0) --manager_press--> MANAGER (4)
    PROMPT (1) --green_press / record(True)--> THANKS (2)
    PROMPT (1) --red_press / record(False)--> THANKS (2)
    PROMPT (1) --timer_timeout--> IDLE (0)
    THANKS (2) --timer_timeout--> [is_low] ALARM (3) / [else] IDLE (0)
    ALARM (3) --manager_press--> MANAGER (4)
    MANAGER (4) --red_press / reset (internal transition)
    MANAGER (4) --green_press, manager_press, timer_timeout--> IDLE (0)

StateModel has no guards or transition actions, so:
  - transition actions on PROMPT's arrows run in stateLeft(PROMPT, event)
  - the choice after THANKS runs in stateEvent and calls gotoState()
  - MANAGER's red_press internal transition runs in stateEvent
"""

from Log import *
from StateModel import *
from Counters import SoftwareTimer
from Button import Button
from Displays import LCDDisplay
from LightStrip import LightStrip
from Buzzer import PassiveBuzzer
from FeedbackStats import FeedbackStats
from KioskView import KioskView
from ProximitySensor import ProximitySensor


class KioskController:
    """
    Builds the kiosk's model, view, inputs, and StateModel, and handles the
    StateModel callbacks (entry, exit, in-state events, and do-activities).
    """

    IDLE = 0
    PROMPT = 1
    THANKS = 2
    ALARM = 3
    MANAGER = 4
    LOW_PCT = 30
    MIN_VOTES = 5

    def __init__(self):
        """Create the hardware, model, view, and StateModel with its transitions."""
        self._view = KioskView(
            LCDDisplay(sda=0, scl=1),
            LightStrip(pin=2, name="Ring", numleds=8, brightness=0.4),
            PassiveBuzzer(16, name="Buzzer"),
        )
        self._stats = FeedbackStats()
        self._model = StateModel(5, self, debug=True)

        self._red = Button(17, "red", handler=None)
        self._green = Button(18, "green", handler=None)
        self._manager = Button(19, "manager", handler=None)
        self._sensor = ProximitySensor(trigger=3, echo=4, name="proximity", threshold=10)
        self._timer = SoftwareTimer(name="timer", handler=None)

        self._model.addButton(self._red)
        self._model.addButton(self._green)
        self._model.addButton(self._manager)
        self._model.addSensor(self._sensor)
        self._model.addTimer(self._timer)

        self._model.addTransition(self.IDLE, ["proximity_trip"], self.PROMPT)
        self._model.addTransition(self.IDLE, ["manager_press"], self.MANAGER)
        self._model.addTransition(self.PROMPT, ["green_press", "red_press"], self.THANKS)
        self._model.addTransition(self.PROMPT, ["timer_timeout"], self.IDLE)
        self._model.addTransition(self.ALARM, ["manager_press"], self.MANAGER)
        self._model.addTransition(self.MANAGER, ["green_press", "manager_press", "timer_timeout"], self.IDLE)

    def stateEntered(self, state, event):
        """Entry actions for each state."""
        Log.i(f"Entered state {state} on {event}")
        pct = self._stats.satisfaction_pct()
        total = self._stats.total()
        if state == self.IDLE:
            self._view.show_idle(pct, total)
        elif state == self.PROMPT:
            self._view.show_prompt()
            self._timer.start(8)
        elif state == self.THANKS:
            self._view.show_thanks(event == "green_press", pct, total)
            self._timer.start(3)
        elif state == self.ALARM:
            self._view.show_alarm(pct)
        elif state == self.MANAGER:
            self._view.show_manager_menu(pct, total)
            self._timer.start(10)

    def stateLeft(self, state, event):
        """Exit actions, plus the transition actions on PROMPT's outgoing arrows."""
        Log.i(f"Left state {state} on {event}")
        if state == self.PROMPT:
            if event in ("green_press", "red_press"):
                self._stats.record(event == "green_press")
            self._timer.cancel()
        elif state == self.THANKS:
            self._timer.cancel()
        elif state == self.ALARM:
            self._view.silence()
        elif state == self.MANAGER:
            self._timer.cancel()

    def stateEvent(self, state, event) -> bool:
        """
        Events with no table transition: the choice after THANKS times out,
        and MANAGER's internal reset on red_press. Returns True if handled.
        """
        if state == self.THANKS and event == "timer_timeout":
            low = self._stats.is_low(self.LOW_PCT, self.MIN_VOTES)
            self._model.gotoState(self.ALARM if low else self.IDLE, event)
            return True
        if state == self.MANAGER and event == "red_press":
            self._stats.reset()
            self._view.show_reset()
            self._timer.start(10)
            return True
        return False

    def stateDo(self, state):
        """Do-activities: the siren keeps sounding while in ALARM."""
        if state == self.ALARM:
            self._view.siren_step()

    def run(self):
        """Start the state model (begins in IDLE and loops until stopped)."""
        self._model.run()

    def stop(self):
        """Stop the state model, its timers, and the siren."""
        self._model.stop()
        self._view.silence()
