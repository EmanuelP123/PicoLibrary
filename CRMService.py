"""
CRMService.py - Mini-Lab 4: IoT CRM Browser
Author: Emanuel Petrini

Proxy for the professor's REST web service. Every request goes through
PicoLibrary's Net.getJson(), and every message is printed with Trace so the
console output matches the sequence diagrams.
"""

from Trace import Trace
from CRMModel import Customer, Contact, Activity


class CRMService:
    """Sends REST messages to the CRM web service and turns the JSON into model objects."""

    def __init__(self, net, base_url):
        """Use an already-created Net object and the web service base URL."""
        self._net = net
        self._base_url = base_url
        self.request_count = 0

    def get_version(self):
        """GET version: return the API version string (or None on failure)."""
        data = self._get("version")
        return data.get("version") if data else None

    def get_customers(self):
        """GET get_customers, following the 'next' page links; return a list of Customer."""
        customers = []
        path = "get_customers"
        while path:
            data = self._get(path)
            if data is None:
                return None
            customers.extend(Customer.from_json(i) for i in data.get("items", []))
            path = None
            if data.get("hasMore"):
                for link in data.get("links", []):
                    if link.get("rel") == "next":
                        path = link["href"].replace(self._base_url, "")
        return customers

    def get_contacts(self, cust_id):
        """GET get_contacts/:cust_id; return a list of Contact."""
        data = self._get(f"get_contacts/{cust_id}")
        return [Contact.from_json(i) for i in data.get("items", [])] if data else []

    def get_activities(self, cust_id):
        """GET get_activities/:cust_id; return a list of Activity."""
        data = self._get(f"get_activities/{cust_id}")
        return [Activity.from_json(i) for i in data.get("items", [])] if data else []

    def _get(self, path):
        """Send one GET through Net, trace the request and reply, and return the JSON dict."""
        url = self._base_url + path
        Trace.call("CRMService", "Net", f"getJson({path})")
        Trace.call("Net", "REST API", f"GET /{path}")
        start = Trace.now()
        data = self._net.getJson(url)
        ms = Trace.since(start)
        self.request_count += 1
        if data is None:
            Trace.reply("Net", "REST API", f"FAILED after {ms} ms")
        else:
            count = data.get("count", 1)
            Trace.reply("Net", "REST API", f"200 OK, {count} item(s), {ms} ms")
        return data
