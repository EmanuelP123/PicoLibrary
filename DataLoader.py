"""
DataLoader.py - Mini-Lab 4: IoT CRM Browser
Author: Emanuel Petrini

The two loading options the lab asks for, as interchangeable strategies:
  A. EagerLoader - get every customer, then every customer's contacts and
     activities, before the user can browse.
  B. LazyLoader  - get the customers only, then get a customer's contacts and
     activities the first time it is selected (and keep them in a cache).
The controller only talks to DataLoader, so it works with either option.
"""

from Trace import Trace


class DataLoader:
    """Abstract loading strategy used by CRMController."""

    MODE = "?"

    def __init__(self, service):
        """Keep the CRMService that sends the REST messages."""
        self._service = service
        self.customers = []
        self.load_ms = 0

    def load_customers(self, progress=None):
        """Load the customer list (and maybe details). Return True on success."""
        raise NotImplementedError

    def ensure_details(self, customer):
        """Make sure a customer's contacts and activities are loaded."""
        raise NotImplementedError

    def _fetch_details(self, customer):
        """Send the two detail requests for one customer and store the results."""
        Trace.call(type(self).__name__, "CRMService", f"get_contacts({customer.id})")
        contacts = self._service.get_contacts(customer.id)
        Trace.call(type(self).__name__, "CRMService", f"get_activities({customer.id})")
        activities = self._service.get_activities(customer.id)
        customer.set_details(contacts, activities)
        Trace.call(type(self).__name__, "Customer",
                   f"set_details({len(contacts)} contacts, {len(activities)} activities)  [{customer.name}]")


class EagerLoader(DataLoader):
    """Option A: load everything up front."""

    MODE = "A"

    def load_customers(self, progress=None):
        """Get all customers, then the contacts and activities of each one."""
        start = Trace.now()
        Trace.call("EagerLoader", "CRMService", "get_customers()")
        customers = self._service.get_customers()
        if customers is None:
            return False
        self.customers = customers
        Trace.reply("EagerLoader", "CRMService", f"{len(customers)} customers")
        for i, customer in enumerate(customers):
            if progress:
                progress(i, len(customers))
            self._fetch_details(customer)
        if progress:
            progress(len(customers), len(customers))
        self.load_ms = Trace.since(start)
        return True

    def ensure_details(self, customer):
        """Nothing to do: option A already loaded every customer's details."""
        Trace.note(f"EagerLoader.ensure_details: already in memory, 0 requests  [{customer.name}]")


class LazyLoader(DataLoader):
    """Option B: load customers first, details on demand (cached)."""

    MODE = "B"

    def load_customers(self, progress=None):
        """Get only the customer list."""
        start = Trace.now()
        if progress:
            progress(0, 1)
        Trace.call("LazyLoader", "CRMService", "get_customers()")
        customers = self._service.get_customers()
        if customers is None:
            return False
        self.customers = customers
        Trace.reply("LazyLoader", "CRMService", f"{len(customers)} customers")
        if progress:
            progress(1, 1)
        self.load_ms = Trace.since(start)
        return True

    def ensure_details(self, customer):
        """Fetch this customer's contacts and activities the first time it is selected."""
        if customer.details_loaded:
            Trace.note(f"LazyLoader.ensure_details: cached, 0 requests  [{customer.name}]")
            return
        start = Trace.now()
        self._fetch_details(customer)
        Trace.note(f"LazyLoader.ensure_details: loaded in {Trace.since(start)} ms  [{customer.name}]")
