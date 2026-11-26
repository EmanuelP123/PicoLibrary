"""
main.py - Mini-Lab 4: IoT CRM Browser
Author: Emanuel Petrini

Entry point. PicoLibrary's own log messages are limited to warnings so the
console shows the sequence trace from Trace.py.
"""

from Log import Log, WARN
from CRMController import CRMController

Log.level = WARN

if __name__ == "__main__":
    app = CRMController()
    try:
        app.run()
    except KeyboardInterrupt:
        app.stop()
