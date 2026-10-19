# Copyright (c) 2025, Akwad and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document


class ScholarshipFlagChangeError(frappe.ValidationError):
    pass


class ScholarshipSubmissionError(frappe.ValidationError):
    pass


class ScholarshipDecisionError(frappe.ValidationError):
    pass


class BeneficiariesRegistration(Document):
    def validate(self):
        self.validate_scholarship_flag_unchanged()
        self.validate_scholarship_leaves_draft_with_request()
        self.validate_scholarship_decided_through_request()
        self.validate_guardian_mobile_number()

    def validate_scholarship_flag_unchanged(self):
        if not self.is_new() and self.has_value_changed("is_scholarship"):
            frappe.throw(
                _("Is Scholarship cannot be changed after the registration is created."),
                ScholarshipFlagChangeError,
            )

    def validate_scholarship_leaves_draft_with_request(self):
        # A scholarship registration must never be submitted without its Beneficiary Request,
        # so only submit_scholarship_application may move it out of Draft.
        if not self.is_scholarship or self.is_new() or self.flags.is_scholarship_submission:
            return

        previous = self.get_doc_before_save()
        if previous and previous.workflow_state == "Draft" and self.workflow_state != "Draft":
            frappe.throw(
                _("A scholarship registration can only be submitted together with its scholarship request."),
                ScholarshipSubmissionError,
            )

    def validate_scholarship_decided_through_request(self):
        # While its scholarship request is pending, the Supervisor decides on the request and the
        # registration follows (plan OQ4). Once the request is closed, the normal workflow applies.
        if not self.is_scholarship or self.is_new() or self.flags.is_scholarship_decision:
            return

        previous = self.get_doc_before_save()
        if not previous or previous.workflow_state == self.workflow_state:
            return
        if self.workflow_state not in ("Accepted", "Not Accepted"):
            return

        pending_request = frappe.db.get_value(
            "Beneficiary Request",
            {"beneficiaries": self.name, "is_scholarship": 1, "workflow_state": "Pending Supervisor Approval"},
        )
        if pending_request:
            frappe.throw(
                _("Approve or reject the scholarship request {0}; this registration follows its decision.").format(
                    pending_request
                ),
                ScholarshipDecisionError,
            )

    def validate_guardian_mobile_number(self):
        if self.guardian_mobile_number and not re.fullmatch(r"\d{8}", self.guardian_mobile_number):
            frappe.throw(_("Guardian Mobile Number must be exactly 8 digits."))
