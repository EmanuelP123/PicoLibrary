# Mini-Lab 3 – AI Prompts (Emanuel Petrini)

## Prompt 1 – Critique of the class model and state model (attach both diagram images)

I'm building a customer "satisfaction kiosk" in MicroPython on a Raspberry Pi Pico (Wokwi first, then a real Pico W) using my fork of PicoLibrary. Attached are my UML class diagram and my UML state diagram. Please critique both before any code is written.

How it should work: the kiosk sits idle until someone comes within 10 cm of an ultrasonic sensor. It then shows "Rate your visit" and enables a green and a red button. Green adds a positive vote, red adds a negative vote, the kiosk thanks the customer and shows the current satisfaction, and after a few seconds it returns to idle. It also returns to idle if nobody votes within a few seconds. If satisfaction falls below 30% (after at least 5 votes), the light strip turns red and an alarm sounds in the manager's office until the manager presses their button. In manager mode, green keeps the statistics and red resets them.

My design decisions:
- KioskController is the handler for PicoLibrary's StateModel. It implements stateEntered, stateLeft, stateEvent, and stateDo. Buttons (green, red, manager), the ultrasonic sensor (proximity), and one SoftwareTimer (timer) are registered with the model, so events arrive as green_press, proximity_trip, timer_timeout, and so on.
- Five states: IDLE, PROMPT, THANKS, ALARM, MANAGER. The low-satisfaction check is a guard in IDLE's do-activity that raises the custom event low_score. The alarm re-arms after the next vote.
- THANKS records the vote in its entry action using the event that caused the transition (green_press or red_press). MANAGER resets the statistics in its exit action only when the event is red_press.
- FeedbackStats is the business model, KioskView owns all hardware output (LCD, light strip, buzzer), and ProximitySensor subclasses PicoLibrary's UltrasonicSensor because distance() returns -1 on a failed reading, which the original tripped() treats as "someone is close."
- For innovation, IDLE shows a satisfaction gauge on the 8-LED light strip (green share vs. red share).
- Customers can't vote while the alarm is active; the kiosk waits for the manager.

Please evaluate: (1) whether the states, events, and transitions cover the requirements and realistic situations (people walking away, repeated presses, sensor noise, an empty kiosk), (2) whether entry, exit, and do actions are in the right places, (3) whether the class responsibilities and relationships are right and the state diagram only uses methods that exist in my class model, and (4) anything that won't work with PicoLibrary's StateModel or MicroPython on the Pico. Don't write code yet. List suggested changes and explain why, so I can decide which ones to adopt.

## Prompt 2 – Model, view, and sensor classes (attach the REVISED class diagram)

I updated both diagrams after your critique (revised class diagram attached). Changes I adopted: IDLE→MANAGER on manager_press; the low-score check is now a choice after THANKS times out instead of a polling do-activity in IDLE (so the low_score custom event and _alarm_acknowledged are gone); votes are recorded as transition actions on PROMPT's arrows; MANAGER's reset is an internal transition on red_press so "Stats reset" stays readable; PROMPT no longer leaves on proximity_untrip; show_gauge is now the private helper _show_gauge; ProximitySensor's constructor is keyword-only; and the state actions call _stats.satisfaction_pct() and _stats.total() directly.

Now implement the non-controller classes from the attached class diagram in MicroPython, using my fork of PicoLibrary (already in the project). Do not modify any PicoLibrary file. Class names, attributes, and methods must match the diagram exactly; tell me before adding or changing anything so I can update the diagram. Docstrings on every class and method.

- FeedbackStats.py: FeedbackStats keeps _positive and _negative counts. satisfaction_pct() returns an int from 0 to 100, and 100 when total() is 0 (no division by zero). is_low(threshold, min_votes) is True only when total() >= min_votes and satisfaction_pct() < threshold.
- ProximitySensor.py: ProximitySensor subclasses UltrasonicSensor from Sensors_advanced.py. __init__(self, *, trigger, echo, name, threshold) passes everything to super().__init__ as keyword arguments. tripped() takes one distance() reading and returns True only when 0 <= distance < threshold, so a failed reading (-1) never counts as a person.
- KioskView.py: KioskView receives LCDDisplay, LightStrip, and PassiveBuzzer in its constructor. _write() pads or truncates both 16-character LCD lines. show_idle() writes the idle screen ("No votes yet" when total is 0) and calls _show_gauge(). _show_gauge() lights round(pct * 8 / 100) LEDs green and the rest red at low brightness, or all LEDs dim blue when total is 0. show_prompt() lights the left half green and the right half red. show_manager_menu(pct, total) shows the score and "Grn=done Red=reset". siren_step() is non-blocking: each call alternates the buzzer between two tones and flips the strip between red and off, using _siren_high. silence() stops the buzzer. Use the color constants from Lights.py and PassiveBuzzer.beep() for short sounds.

## Prompt 3 – State model controller and main.py (attach BOTH revised diagrams)

Now implement KioskController.py exactly as my attached revised state diagram shows, following the structure of PicoLibrary's ModelTemplate.py, plus main.py. First write implementation_plan.md describing how each state, event, transition, guard, and action is handled, and wait for my approval.

Hardware (matches my Wokwi diagram.json):
- LCDDisplay(sda=0, scl=1); LightStrip(pin=2, numleds=8); PassiveBuzzer(16)
- Button(17, "red", handler=None), Button(18, "green", handler=None), Button(19, "manager", handler=None)
- ProximitySensor(trigger=3, echo=4, name="proximity", threshold=10)
- SoftwareTimer(name="timer", handler=None)

Controller rules:
- Create StateModel(5, self, debug=True). Register the three buttons, the sensor, and the timer with addButton, addSensor, and addTimer before adding transitions. Use the state constants IDLE=0, PROMPT=1, THANKS=2, ALARM=3, MANAGER=4.
- Transition table (addTransition), exactly: IDLE→PROMPT on proximity_trip; IDLE→MANAGER on manager_press; PROMPT→THANKS on green_press or red_press; PROMPT→IDLE on timer_timeout; ALARM→MANAGER on manager_press; MANAGER→IDLE on green_press, manager_press, or timer_timeout. THANKS has no table transition.
- PicoLibrary's StateModel has no guards or transition actions, so implement them like this:
  - Transition actions: in stateLeft, when state == PROMPT and event is green_press or red_press, call _stats.record(event == "green_press") before cancelling the timer. stateLeft runs before stateEntered, so THANKS shows the updated stats.
  - The choice after THANKS: in stateEvent, when state == THANKS and event == "timer_timeout", call self._model.gotoState(ALARM if _stats.is_low(LOW_PCT, MIN_VOTES) else IDLE, event) and return True.
  - MANAGER's internal transition: in stateEvent, when state == MANAGER and event == "red_press", call _stats.reset(), _view.show_reset(), and _timer.start(10), and return True.
  - stateEvent returns False for every other event.
- Entry, exit, and do actions exactly as written in each state of the diagram (timers 8 s, 3 s, 10 s). ALARM's do-activity calls _view.siren_step() from stateDo.
- run() calls self._model.run(); stop() calls self._model.stop(). main.py creates KioskController and calls run().
- Use Log.i() for key events. Keep everything object-oriented, with docstrings.
