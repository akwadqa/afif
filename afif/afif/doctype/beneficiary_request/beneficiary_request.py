# Copyright (c) 2025, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

SCHOLARSHIP_ATTACHMENT_FIELDS = (
    "education_invoice",
    "grade_transcript",
    "scholarship_guardian_id",
    "scholarship_guardian_passport",
    "scholarship_student_id",
    "scholarship_student_passport",
    "scholarship_family_ids",
    "scholarship_guardian_bank_statement",
)
SCHOLARSHIP_DECLARATION_FIELDS = ("is_data_accuracy_declared", "is_eligibility_check_accepted")


class ScholarshipFlagChangeError(frappe.ValidationError):
    pass


class IncompleteScholarshipRequestError(frappe.ValidationError):
    pass


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
        self.validate_scholarship_flag()
        self.validate_scholarship_request()

    def validate_request_summary(self):
        if self.request_summary and len(self.request_summary) > 1000:
            frappe.throw(
                _("Request Summary cannot be more than 1000 characters")
            )

    @property
    def is_scholarship_subcategory(self) -> bool:
        return self.request_category == "Education Assistance" and self.educational_assistance == "Scholarship"

    def validate_scholarship_flag(self):
        # The flag drives the registration cascade, so only the scholarship endpoint may set it.
        if self.is_new():
            if self.is_scholarship and not self.flags.is_scholarship_submission:
                frappe.throw(
                    _("Scholarship requests can only be created through the scholarship application."),
                    ScholarshipFlagChangeError,
                )
        elif self.has_value_changed("is_scholarship"):
            frappe.throw(_("Is Scholarship cannot be changed after the request is created."), ScholarshipFlagChangeError)

    def validate_scholarship_request(self):
        if not self.is_scholarship_subcategory:
            return

        missing = self.get_missing_scholarship_fields()
        if missing:
            frappe.throw(
                _("The scholarship request is incomplete. Missing: {0}").format(", ".join(missing)),
                IncompleteScholarshipRequestError,
            )

    def get_missing_scholarship_fields(self) -> list[str]:
        required = [*SCHOLARSHIP_ATTACHMENT_FIELDS, *SCHOLARSHIP_DECLARATION_FIELDS]
        missing = [fieldname for fieldname in required if not self.get(fieldname)]
        if not (self.request_summary or "").strip():
            missing.insert(0, "request_summary")
        if flt(self.requested_amount) <= 0:
            missing.insert(0, "requested_amount")
        return [_(self.meta.get_label(fieldname)) for fieldname in missing]


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
