# Copyright (c) 2025, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class BeneficiaryRequest(Document):
    def validate(self):
        if self.request_summary and len(self.request_summary) > 1000:
            frappe.throw(_("Request Summary cannot be more than 1000 characters"))
