# Copyright (c) 2025, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class BeneficiaryRequest(Document):
    @frappe.whitelist()
    def check_beneficiary_id(self):

        beneficiary = frappe.get_doc("Beneficiaries Registration", self.beneficiaries)
        
        if not beneficiary.ben_id:
            frappe.log_error(f"beneficiary {beneficiary.name} didn\'t get id from Sanadi")
            return {
                "success": False,
                "message": _("This beneficiary didn't get ID from Sanadi")
            }   

        return {
            "success": True
        }
            

    def validate(self):
        self.validate_request_summary()        

    def validate_request_summary(self):
        if self.request_summary and len(self.request_summary) > 1000:
            frappe.throw(
                _("Request Summary cannot be more than 1000 characters")
            )

