import frappe
from frappe.model.document import Document
import requests

class WHMassage(Document):
    def after_insert(self):
        frappe.db.set_value(self.doctype, self.name, "type", "out")
        