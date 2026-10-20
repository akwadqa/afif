# Copyright (c) 2025, Akwad and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document

# All of them are required to submit a scholarship application (plan Phase 6).
SCHOLARSHIP_ATTACHMENT_FIELDS = (
    "scholarship_university_invoice",
    "scholarship_grade_transcript",
    "scholarship_guardian_id",
    "scholarship_guardian_passport",
    "scholarship_student_id",
    "scholarship_student_passport",
    "scholarship_family_ids",
    "scholarship_guardian_bank_statement",
    "scholarship_mother_bank_statement",
    "scholarship_student_bank_statement",
)


class ScholarshipFlagChangeError(frappe.ValidationError):
    pass


class ScholarshipSubmissionError(frappe.ValidationError):
    pass


class ScholarshipDecisionError(frappe.ValidationError):
    pass


class SingleMaritalStatusError(frappe.ValidationError):
    pass


class BeneficiariesRegistration(Document):
    def validate(self):
        self.validate_scholarship_flag_unchanged()
        self.validate_scholarship_leaves_draft_with_request()
        self.validate_scholarship_decided_through_request()
        self.validate_guardian_mobile_number()
        self.validate_single_marital_status()

    def on_update(self):
        self.delete_replaced_attachments()

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
        # An already accepted beneficiary's scholarship request does not decide their registration.
        if not previous or previous.workflow_state != "New Registration":
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

    def validate_single_marital_status(self):
        # Single is offered to scholarship applicants only; a few older registrations already hold it
        # and can still be saved, so only setting it is refused.
        if self.is_scholarship or self.marital_status != "Single":
            return
        if self.is_new() or self.has_value_changed("marital_status"):
            frappe.throw(
                _("Marital status Single is only available for scholarship applications."),
                SingleMaritalStatusError,
            )

    def delete_replaced_attachments(self):
        """Delete the File of an attachment that was replaced or cleared, so it does not stay behind."""
        previous = self.get_doc_before_save()
        if not previous:
            return

        for df in self.meta.get("fields", {"fieldtype": ("in", ("Attach", "Attach Image"))}):
            old_file_url = previous.get(df.fieldname)
            if not old_file_url or old_file_url == self.get(df.fieldname):
                continue

            # Only this field's File: Frappe reuses one file_url for identical uploads, and the
            # disk copy is kept while another File still points at it.
            replaced_files = frappe.get_all(
                "File",
                filters={
                    "attached_to_doctype": self.doctype,
                    "attached_to_name": self.name,
                    "attached_to_field": df.fieldname,
                    "file_url": old_file_url,
                },
                pluck="name",
            )
            for file_name in replaced_files:
                # The save already checked that the user may change this registration.
                frappe.delete_doc("File", file_name, ignore_permissions=True)
