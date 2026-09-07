# Copyright (c) 2025, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class BeneficiaryRequest(Document):
    @frappe.whitelist()
    def check_beneficiary_id(self):

        beneficiary = frappe.get_doc("Beneficiaries Registration", self.beneficiaries)
        
        if not beneficiary.ben_id or beneficiary.ben_id == "akwad":
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


@frappe.whitelist()
def send_visit_sms(request_name):
    frappe.has_permission("Beneficiary Request", "read", throw=True)

    phone_number = frappe.get_value("Beneficiary Request", request_name, "phone_number")
    if not phone_number:
        frappe.throw(_("No phone number on file for this request."))

    message = frappe.db.get_single_value("SMS Settings", "visit_sms_message")
    if not message:
        frappe.throw(
            _("Visit SMS message is not configured. Please set it in SMS Settings.")
        )

    from frappe.core.doctype.sms_settings.sms_settings import send_sms

    send_sms(receiver_list=[phone_number], msg=message, success_msg=False)

    return {"sent": True}
