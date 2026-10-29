# Copyright (c) 2025, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from afif.hooks_call import get_aid_lookup_parent_id

SCHOLARSHIP_DECLARATION_FIELDS = ("is_data_accuracy_declared", "is_eligibility_check_accepted")


class ScholarshipFlagChangeError(frappe.ValidationError):
    pass


class ScholarshipSubcategoryError(frappe.ValidationError):
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
        self.validate_scholarship_subcategory()
        self.validate_scholarship_request()
        self.validate_scholarship_aid_lookup()

        # Only on insert, so existing incomplete requests stay editable by staff
        if self.is_new():
            self.validate_required_attachments()

    def on_update(self):
        # Runs before the on_update hooks, so the registration has its Sanadi id before
        # new_subvention_request sends this request to Sanadi.
        self.accept_scholarship_registration_with_request()

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

    def validate_scholarship_subcategory(self):
        # Scholarship is applied for only through /scholarship, which sets the flag (plan Phase 6), so a
        # request carries the subcategory exactly when it carries the flag.
        if self.is_scholarship_subcategory and not self.is_scholarship:
            frappe.throw(
                _("Scholarship requests can only be created through the scholarship application."),
                ScholarshipSubcategoryError,
            )
        if self.is_scholarship and not self.is_scholarship_subcategory:
            frappe.throw(
                _("A scholarship request must stay Education Assistance - Scholarship."),
                ScholarshipSubcategoryError,
            )

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
        missing = [fieldname for fieldname in SCHOLARSHIP_DECLARATION_FIELDS if not self.get(fieldname)]
        if not (self.request_summary or "").strip():
            missing.insert(0, "request_summary")
        if flt(self.requested_amount) <= 0:
            missing.insert(0, "requested_amount")
        return [_(self.meta.get_label(fieldname)) for fieldname in missing]

    @property
    def is_scholarship_supervisor_approval(self) -> bool:
        previous = self.get_doc_before_save()
        return bool(
            self.is_scholarship
            and previous
            and previous.workflow_state == "Pending Supervisor Approval"
            and self.workflow_state == "Pending Specialist Approval"
        )

    def validate_scholarship_aid_lookup(self):
        # Fail on a missing Sanadi mapping before anything is sent to Sanadi.
        if self.is_scholarship_supervisor_approval:
            get_aid_lookup_parent_id(self)

    def accept_scholarship_registration_with_request(self):
        """Accept the linked registration when the Supervisor approves its scholarship request (plan D11).

        A rejection only rejects the request, as in the normal request flow: the registration is left
        as it is, and the Supervisor decides it through its own workflow (plan Phase 8).
        """
        if not self.is_scholarship_supervisor_approval:
            return

        registration = frappe.get_doc("Beneficiaries Registration", self.beneficiaries)
        if registration.workflow_state == "New Registration":
            registration.workflow_state = registration.status = "Accepted"
            registration.flags.is_scholarship_decision = True
            # The Supervisor's right to decide was checked on the request; the registration's own
            # workflow transition check still runs.
            registration.save(ignore_permissions=True)

        if not frappe.db.get_value("Beneficiaries Registration", registration.name, "ben_id"):
            frappe.throw(
                _("The beneficiary could not be registered in Sanadi, so the scholarship request was not approved."),
                ScholarshipCascadeError,
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
