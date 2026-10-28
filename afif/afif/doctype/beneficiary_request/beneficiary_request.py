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
        # Only on insert, so existing incomplete requests stay editable by staff
        if self.is_new():
            self.validate_required_attachments()

    def validate_request_summary(self):
        if self.request_summary and len(self.request_summary) > 1000:
            frappe.throw(
                _("Request Summary cannot be more than 1000 characters")
            )

    def validate_required_attachments(self):
        missing = self.get_missing_required_attachments()
        if not missing:
            return

        labels = "".join(f"<li>{_(self.meta.get_label(field))}</li>" for field in missing)
        frappe.throw(
            _("Please upload the following required documents:") + f"<ul>{labels}</ul>",
            title=_("Missing Attachments"),
        )

    def get_missing_required_attachments(self) -> list[str]:
        """Server-side mirror of the attachments' `mandatory_depends_on`, which Frappe only evaluates in the browser."""
        is_medical = self.request_category == "Medical Assistance"
        is_education = self.request_category == "Education Assistance" and self.educational_assistance != "Scholarship"
        is_social = self.request_category == "Social Assistance"
        is_garmeen = is_social and self.social_assistance == "Garmeen"
        is_housing = self.request_category == "Housing Assistance"

        required = {
            "medical_bill": is_medical,
            "education_invoice": is_education,
            "grade_transcript": is_education,
            "garmeen_proof": is_garmeen,
            "garmeen_disclosure": is_garmeen,
            "travel_ticket_doc": is_social and self.social_assistance == "Travel ticket assistance",
            "rent_contract": is_housing,
            "onwer_qid": is_housing,
            "late_letter": is_housing,
            "estate_pruchase": is_housing and self.housing_assistance == "Real estate purchase",
        }
        return [field for field, is_required in required.items() if is_required and not self.get(field)]


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
