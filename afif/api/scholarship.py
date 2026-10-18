import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

from afif.afif.doctype.beneficiary_request.beneficiary_request import (
    SCHOLARSHIP_ATTACHMENT_FIELDS,
    SCHOLARSHIP_DECLARATION_FIELDS,
)
from afif.api.response import gen_response
from afif.hooks_call import get_missing_required_attachments

REGISTRATION_CONSENT_FIELDS = ("documents_confirmation", "verification_consent", "cancellation_right")
REQUEST_INPUT_FIELDS = (
    "requested_amount",
    "request_summary",
    *SCHOLARSHIP_ATTACHMENT_FIELDS,
    *SCHOLARSHIP_DECLARATION_FIELDS,
)


class IncompleteScholarshipApplicationError(frappe.ValidationError):
    pass


@frappe.whitelist(methods=["POST"])
def submit_scholarship_application(registration: str, request: dict | str) -> None:
    """Submit a scholarship Draft registration and create its Beneficiary Request in one transaction."""
    request = frappe.parse_json(request)
    registration_doc = get_own_scholarship_draft(registration)
    validate_registration_complete(registration_doc)

    request_doc = build_scholarship_request(registration_doc, request)
    request_doc.validate_scholarship_request()
    request_files = get_unattached_own_files(request_doc)

    # Everything is validated before the first write, so a failure leaves both documents untouched.
    registration_doc.flags.is_scholarship_submission = True
    apply_workflow(registration_doc, "Submit")
    # Not-yet-accepted beneficiaries have no create permission on requests; ownership of the
    # registration and of every file was checked above.
    request_doc.insert(ignore_permissions=True)
    attach_files_to_request(request_files, request_doc)

    gen_response(
        200,
        _("Scholarship application submitted"),
        {"registration": registration_doc.name, "request": request_doc.name},
    )


def get_own_scholarship_draft(registration: str) -> Document:
    registration_doc = frappe.get_doc("Beneficiaries Registration", registration)
    if registration_doc.user != frappe.session.user:
        raise frappe.PermissionError(_("You can only submit your own registration."))
    if not registration_doc.is_scholarship:
        frappe.throw(_("This registration was not started as a scholarship application."))
    if registration_doc.workflow_state != "Draft":
        frappe.throw(_("This scholarship application has already been submitted."))
    return registration_doc


def validate_registration_complete(registration_doc: Document) -> None:
    missing = get_missing_required_attachments(registration_doc)
    missing += [fieldname for fieldname in REGISTRATION_CONSENT_FIELDS if not registration_doc.get(fieldname)]
    if missing:
        labels = [_(registration_doc.meta.get_label(fieldname)) for fieldname in missing]
        frappe.throw(
            _("The registration is incomplete. Missing: {0}").format(", ".join(labels)),
            IncompleteScholarshipApplicationError,
        )


def build_scholarship_request(registration_doc: Document, request: dict) -> Document:
    request_doc = frappe.new_doc("Beneficiary Request")
    request_doc.update({fieldname: request.get(fieldname) for fieldname in REQUEST_INPUT_FIELDS})
    request_doc.update(
        {
            "request_category": "Education Assistance",
            "educational_assistance": "Scholarship",
            "is_scholarship": 1,
            "beneficiaries": registration_doc.name,
        }
    )
    request_doc.flags.is_scholarship_submission = True
    return request_doc


def get_unattached_own_files(request_doc: Document) -> dict[str, str]:
    """Map each attachment field to a File the session user uploaded and has not attached anywhere yet.

    Without this check a user could point the request at somebody else's uploaded documents.
    """
    files = {}
    for fieldname in SCHOLARSHIP_ATTACHMENT_FIELDS:
        filters = {
            "file_url": request_doc.get(fieldname),
            "owner": frappe.session.user,
            "attached_to_name": ("is", "not set"),
        }
        if files:
            filters["name"] = ("not in", list(files.values()))

        file_name = frappe.db.get_value("File", filters, "name")
        if not file_name:
            raise frappe.PermissionError(
                _("The file for {0} was not uploaded by you or is already in use.").format(
                    _(request_doc.meta.get_label(fieldname))
                )
            )
        files[fieldname] = file_name
    return files


def attach_files_to_request(request_files: dict[str, str], request_doc: Document) -> None:
    for fieldname, file_name in request_files.items():
        file_doc = frappe.get_doc("File", file_name)
        file_doc.update(
            {
                "attached_to_doctype": request_doc.doctype,
                "attached_to_name": request_doc.name,
                "attached_to_field": fieldname,
            }
        )
        file_doc.save()
