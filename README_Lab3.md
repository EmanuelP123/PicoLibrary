# Mini-Lab 3 – Satisfaction Kiosk (Emanuel Petrini)

A customer satisfaction kiosk for the Raspberry Pi Pico W, built on PicoLibrary's `StateModel`.

When someone comes within 10 cm of the ultrasonic sensor, the kiosk asks them to rate their visit with a green or red button, thanks them, and shows the current satisfaction. If satisfaction drops below 30% (after at least 5 votes), the light strip flashes red and a siren sounds until the manager presses their button; the manager can then keep or reset the statistics. While idle, the 8-LED strip works as a live satisfaction gauge.

## States
IDLE → PROMPT → THANKS → (ALARM →) MANAGER → IDLE. See `Lab3_state_diagram.pdf`.

## Hardware (Wokwi: https://wokwi.com/projects/480621300390449153)
| Part | Pico GP |
|---|---|
| LCD SDA / SCL | GP0 / GP1 |
| Light strip DIN | GP2 |
| HC-SR04 TRIG / ECHO | GP3 / GP4 |
| Passive buzzer | GP16 |
| Red / Green / Manager buttons | GP17 / GP18 / GP19 |

## Files for this lab
- `Lab3_class_diagram.pdf`, `Lab3_state_diagram.pdf` – UML models (revised after AI critique)
- `Lab3_prompts.md` – prompts used with Antigravity
- My code (added when implemented): `main.py`, `KioskController.py`, `FeedbackStats.py`, `KioskView.py`, `ProximitySensor.py`
