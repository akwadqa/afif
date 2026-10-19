# Copyright (c) 2025, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from afif.hooks_call import get_aid_lookup_parent_id

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
# The Supervisor's decision on a scholarship request, and the registration state it carries over to.
SUPERVISOR_DECISION_REGISTRATION_STATES = {
    "Pending Specialist Approval": "Accepted",
    "Rejected by Supervisor": "Not Accepted",
}


class ScholarshipFlagChangeError(frappe.ValidationError):
    pass


class IncompleteScholarshipRequestError(frappe.ValidationError):
    pass


class ScholarshipCascadeError(frappe.ValidationError):
    pass


class BeneficiaryRequest(Document):
    @frappe.whitelist()
    def check_beneficiary_id(self):

        beneficiary = frappe.get_doc("Beneficiaries Registration", self.beneficiaries)

        if self.is_scholarship and beneficiary.workflow_state == "New Registration":
            # Approving the request accepts the registration, which gets its Sanadi id in the same action.
            return {"success": True}

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
        self.validate_scholarship_aid_lookup()

    def on_update(self):
        # Runs before the on_update hooks, so the registration has its Sanadi id before
        # new_subvention_request sends this request to Sanadi.
        self.apply_supervisor_decision_to_scholarship_registration()

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

    @property
    def is_scholarship_supervisor_decision(self) -> bool:
        previous = self.get_doc_before_save()
        return bool(
            self.is_scholarship
            and previous
            and previous.workflow_state == "Pending Supervisor Approval"
            and self.workflow_state in SUPERVISOR_DECISION_REGISTRATION_STATES
        )

    def validate_scholarship_aid_lookup(self):
        # Fail on a missing Sanadi mapping before anything is sent to Sanadi.
        if self.is_scholarship_supervisor_decision and self.workflow_state == "Pending Specialist Approval":
            get_aid_lookup_parent_id(self)

    def apply_supervisor_decision_to_scholarship_registration(self):
        """Accept or reject the linked registration together with its scholarship request (plan D9, D11)."""
        if not self.is_scholarship_supervisor_decision:
            return

        registration = frappe.get_doc("Beneficiaries Registration", self.beneficiaries)
        if registration.workflow_state == "New Registration":
            registration.workflow_state = registration.status = SUPERVISOR_DECISION_REGISTRATION_STATES[
                self.workflow_state
            ]
            if registration.workflow_state == "Not Accepted":
                registration.custom_notes = _("Scholarship request {0} was rejected.").format(self.name)
            registration.flags.is_scholarship_decision = True
            # The Supervisor's right to decide was checked on the request; the registration's own
            # workflow transition check still runs.
            registration.save(ignore_permissions=True)

        if self.workflow_state == "Pending Specialist Approval" and not frappe.db.get_value(
            "Beneficiaries Registration", registration.name, "ben_id"
        ):
            frappe.throw(
                _("The beneficiary could not be registered in Sanadi, so the scholarship request was not approved."),
                ScholarshipCascadeError,
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
