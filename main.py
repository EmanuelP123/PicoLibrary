"""
main.py - Mini-Lab 3: Satisfaction Kiosk
Author: Emanuel Petrini

Entry point: creates the kiosk controller and runs its state model.
"""

from KioskController import KioskController

if __name__ == "__main__":
    kiosk = KioskController()
    try:
        kiosk.run()
    except KeyboardInterrupt:
        kiosk.stop()
