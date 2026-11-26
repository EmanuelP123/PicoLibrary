"""
CRMController.py - Mini-Lab 4: IoT CRM Browser
Author: Emanuel Petrini

Controller and StateModel handler (structure from PicoLibrary's ModelTemplate.py).

States:
  MODE (0)       pick option A (Prev) or B (Next)
  LOADING (1)    connect WiFi, load customers with the chosen DataLoader
  CUSTOMERS (2)  Prev/Next browse customers, Select -> CONTACTS
  CONTACTS (3)   loads details if needed (option B), Prev/Next browse, Select -> ACTIVITIES
  ACTIVITIES (4) Prev/Next browse, Select -> CUSTOMERS
Network work runs in stateDo, not in button callbacks.
"""

from Log import *
from StateModel import StateModel
from Button import Button
from Displays import LCDDisplay
from LightStrip import LightStrip
from Buzzer import PassiveBuzzer
from Net import Net
from Trace import Trace
from CRMService import CRMService
from CRMView import CRMView
from DataLoader import EagerLoader, LazyLoader
import config


class CRMController:
    """Builds the app and drives it through PicoLibrary's StateModel."""

    MODE = 0
    LOADING = 1
    CUSTOMERS = 2
    CONTACTS = 3
    ACTIVITIES = 4

    def __init__(self):
        """Create the hardware, network, service, view, and the state model."""
        self._view = CRMView(LCDDisplay(sda=0, scl=1),
                             LightStrip(pin=2, name="Ring", numleds=8, brightness=0.2),
                             PassiveBuzzer(16, name="Buzzer"))
        self._net = Net()
        self._service = CRMService(self._net, config.BASE_URL)
        self._loader = None
        self._cust_index = 0
        self._item_index = 0
        self._busy = False

        self._model = StateModel(5, self, debug=False)
        self._model.addButton(Button(17, "prev", handler=None))
        self._model.addButton(Button(18, "next", handler=None))
        self._model.addButton(Button(19, "select", handler=None))
        self._model.addCustomEvent("loaded")
        self._model.addCustomEvent("load_failed")

        self._model.addTransition(self.MODE, ["prev_press", "next_press"], self.LOADING)
        self._model.addTransition(self.LOADING, ["loaded"], self.CUSTOMERS)
        self._model.addTransition(self.LOADING, ["load_failed"], self.MODE)
        self._model.addTransition(self.CUSTOMERS, ["select_press"], self.CONTACTS)
        self._model.addTransition(self.CONTACTS, ["select_press"], self.ACTIVITIES)
        self._model.addTransition(self.ACTIVITIES, ["select_press"], self.CUSTOMERS)

    # ---------- StateModel callbacks ----------

    def stateEntered(self, state, event):
        """Entry actions."""
        if state == self.MODE:
            self._view.show_mode_menu()
        elif state == self.LOADING:
            self._busy = True
            self._view.show_progress("Connecting WiFi", 0, 1)
        elif state == self.CUSTOMERS:
            self._show_customer()
        elif state == self.CONTACTS:
            self._item_index = 0
            customer = self._current()
            Trace.call("User", "CRMController", f"select customer [{customer.name}]")
            if customer.details_loaded:
                self._show_contact()
            else:
                self._busy = True
                self._view.show_progress("Loading details", 0, 2)
        elif state == self.ACTIVITIES:
            self._item_index = 0
            self._show_activity()

    def stateLeft(self, state, event):
        """Exit actions: leaving MODE picks the loading strategy."""
        if state == self.MODE and event in ("prev_press", "next_press"):
            loader_class = EagerLoader if event == "prev_press" else LazyLoader
            self._loader = loader_class(self._service)
            Trace.reset()
            Trace.note(f"Option {self._loader.MODE} selected ({loader_class.__name__})")

    def stateEvent(self, state, event):
        """In-state events: Prev/Next browse the current list."""
        if self._busy or event not in ("prev_press", "next_press"):
            return False
        step = 1 if event == "next_press" else -1
        if state == self.CUSTOMERS:
            self._cust_index = (self._cust_index + step) % len(self._loader.customers)
            self._show_customer()
            return True
        if state in (self.CONTACTS, self.ACTIVITIES):
            customer = self._current()
            items = customer.contacts if state == self.CONTACTS else customer.activities
            if items:
                self._item_index = (self._item_index + step) % len(items)
            if state == self.CONTACTS:
                self._show_contact()
            else:
                self._show_activity()
            return True
        return False

    def stateDo(self, state):
        """Do-activities: the network work for LOADING and (option B) CONTACTS."""
        if state == self.LOADING and self._busy:
            self._busy = False
            self._model.processEvent("loaded" if self._load_all() else "load_failed")
        elif state == self.CONTACTS and self._busy:
            customer = self._current()
            Trace.call("CRMController", type(self._loader).__name__, f"ensure_details({customer.id})")
            self._loader.ensure_details(customer)
            self._busy = False
            self._show_contact()

    # ---------- helpers ----------

    def _load_all(self):
        """Connect to WiFi, check the API, and load the customers with the chosen loader."""
        try:
            if not self._net.isConnected():
                Trace.call("CRMController", "Net", f"connect({config.WIFI_SSID})")
                self._net.connect(config.WIFI_SSID, config.WIFI_PASSWORD, max_wait=30)
                print()
                Trace.reply("CRMController", "Net", f"connected, IP {self._net.getLocalIp()}")
        except Exception as e:
            Log.e(f"WiFi failed: {e}")
            self._view.show_error("WiFi failed")
            return False
        Trace.call("CRMController", "CRMService", "get_version()")
        version = self._service.get_version()
        Trace.reply("CRMController", "CRMService", f"API version {version}")
        if version is None:
            self._view.show_error("API unreachable")
            return False

        self._service.request_count = 0
        name = type(self._loader).__name__
        Trace.call("CRMController", name, "load_customers()")
        ok = self._loader.load_customers(
            lambda done, total: self._view.show_progress(f"Loading opt {self._loader.MODE}", done, total))
        if not ok or not self._loader.customers:
            self._view.show_error("No customers")
            return False
        seconds = self._loader.load_ms / 1000
        Trace.reply("CRMController", name,
                    f"{len(self._loader.customers)} customers in {seconds:.1f} s, " +
                    f"{self._service.request_count} REST calls")
        self._cust_index = self._find_my_customer()
        self._view.show_ready(self._loader.MODE, len(self._loader.customers), seconds,
                              self._service.request_count)
        return True

    def _find_my_customer(self):
        """Start the browser on my own customer entry if it exists."""
        for i, c in enumerate(self._loader.customers):
            if c.name == config.MY_CUSTOMER:
                return i
        return 0

    def _current(self):
        """The currently selected customer."""
        return self._loader.customers[self._cust_index]

    def _show_customer(self):
        """Show the current customer."""
        self._view.show_customer(self._current(), self._cust_index, len(self._loader.customers))

    def _show_contact(self):
        """Show the current contact of the selected customer."""
        c = self._current()
        item = c.contacts[self._item_index] if c.contacts else None
        if item:
            Trace.note(f"show contact {self._item_index + 1}/{len(c.contacts)}: {item.name}, {item.title}")
        self._view.show_contact(c, item, self._item_index, len(c.contacts))

    def _show_activity(self):
        """Show the current activity of the selected customer."""
        c = self._current()
        item = c.activities[self._item_index] if c.activities else None
        if item:
            Trace.note(f"show activity {self._item_index + 1}/{len(c.activities)}: " +
                       f"{item.name} ({item.activity_type}, {item.short_date()})")
        self._view.show_activity(c, item, self._item_index, len(c.activities))

    def run(self):
        """Start the state model."""
        self._model.run()

    def stop(self):
        """Stop the state model."""
        self._model.stop()
