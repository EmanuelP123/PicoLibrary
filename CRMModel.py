"""
CRMModel.py - Mini-Lab 4: IoT CRM Browser
Author: Emanuel Petrini

Business model classes built from the JSON returned by the CRM web service.
"""


class Contact:
    """A person who works for a customer (get_contacts/:cust_id)."""

    def __init__(self, contact_id, name, title, phone, contact_type):
        """Create a contact from its fields."""
        self.id = contact_id
        self.name = name
        self.title = title
        self.phone = phone
        self.contact_type = contact_type

    @staticmethod
    def from_json(item):
        """Build a Contact from one JSON item of get_contacts."""
        return Contact(item.get("id"), item.get("name") or "", item.get("title") or "",
                       item.get("phone") or "", item.get("contact_type") or "")


class Activity:
    """Something our business did with a customer (get_activities/:cust_id)."""

    def __init__(self, activity_id, activity_type, name, description, date, owner, location):
        """Create an activity from its fields."""
        self.id = activity_id
        self.activity_type = activity_type
        self.name = name
        self.description = description
        self.date = date
        self.owner = owner
        self.location = location

    @staticmethod
    def from_json(item):
        """Build an Activity from one JSON item of get_activities."""
        return Activity(item.get("id"), item.get("activity_type") or "", item.get("name") or "",
                        item.get("description") or "", item.get("activity_date") or "",
                        item.get("owner") or "", item.get("location") or "")

    def short_date(self):
        """Return the date as MM/DD/YY, or '' if there is none."""
        d = self.date
        if len(d) >= 10:
            return f"{d[5:7]}/{d[8:10]}/{d[2:4]}"
        return d


class Customer:
    """A client company or person, with the contacts and activities loaded for it."""

    def __init__(self, customer_id, name, category, geography, cust_type):
        """Create a customer; contacts and activities are loaded later."""
        self.id = customer_id
        self.name = name
        self.category = category
        self.geography = geography
        self.type = cust_type
        self.contacts = []
        self.activities = []
        self.details_loaded = False

    @staticmethod
    def from_json(item):
        """Build a Customer from one JSON item of get_customers."""
        return Customer(item.get("id"), item.get("customer_name") or "", item.get("category") or "",
                        item.get("geography_name") or "", item.get("type") or "")

    def set_details(self, contacts, activities):
        """Store the contacts and activities and mark the details as loaded."""
        self.contacts = contacts
        self.activities = activities
        self.details_loaded = True

    def has_activities(self):
        """True when at least one activity has been loaded for this customer."""
        return len(self.activities) > 0
