import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

from afif.afif.doctype.beneficiary_request.beneficiary_request import (
    SCHOLARSHIP_DECLARATION_FIELDS,
    SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS,
)
from afif.api.response import gen_response

REGISTRATION_CONSENT_FIELDS = ("documents_confirmation", "verification_consent", "cancellation_right")
SCHOLARSHIP_REGISTRATION_REQUIRED_FIELDS = ("passport_number", "guardian_mobile_number", *REGISTRATION_CONSENT_FIELDS)
REQUEST_INPUT_FIELDS = (
    "requested_amount",
    "request_summary",
    *SCHOLARSHIP_DECLARATION_FIELDS,
    *SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS,
)


class IncompleteScholarshipApplicationError(frappe.ValidationError):
    pass


@frappe.whitelist(methods=["POST"])
def submit_scholarship_application(registration: str, request: dict | str) -> None:
    """Submit a scholarship Draft registration and create its Beneficiary Request in one transaction.

    The scholarship documents were uploaded unattached and are attached to the new request.
    """
    registration_doc = get_own_scholarship_draft(registration)
    validate_registration_complete(registration_doc)

    request = frappe.parse_json(request)
    request_doc = new_scholarship_request(request)
    request_doc.beneficiaries = registration_doc.name
    # The registration is submitted in this same transaction, so it is not Accepted yet.
    request_doc.flags.is_new_scholarship_applicant = True
    request_doc.validate_scholarship_request()
    request_files = get_own_unattached_files(request)

    # Everything is validated before the first write, so a failure leaves both documents untouched.
    registration_doc.flags.is_scholarship_submission = True
    apply_workflow(registration_doc, "Submit")
    # Not-yet-accepted beneficiaries have no create permission on requests; ownership of the
    # registration was checked above.
    request_doc.insert(ignore_permissions=True)
    attach_files_to_request(request_files, request_doc)

    gen_response(
        200,
        _("Scholarship application submitted"),
        {"registration": registration_doc.name, "request": request_doc.name},
    )


@frappe.whitelist(methods=["POST"])
def create_scholarship_request(request: dict | str) -> None:
    """Create a new scholarship request for an accepted scholarship beneficiary, with its documents.

    The files are uploaded unattached, before the request exists, and are attached to it here.
    """
    # The scholarship is its own flow: a beneficiary who registered through the normal flow cannot
    # apply for it (plan Phase 7).
    if not frappe.db.get_value("Beneficiaries Registration", {"user": frappe.session.user}, "is_scholarship"):
        raise frappe.PermissionError(_("Only scholarship applicants can file a scholarship request."))

    request = frappe.parse_json(request)
    request_doc = new_scholarship_request(request)
    request_doc.validate_scholarship_request()
    request_files = get_own_unattached_files(request)

    # Normal permissions and before_insert_request apply: accepted beneficiaries only, and the
    # pending-request and cooldown rules (OQ5). before_insert_request sets the registration.
    request_doc.insert()
    attach_files_to_request(request_files, request_doc)

    gen_response(200, _("Scholarship request submitted"), {"request": request_doc.name})


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
    missing = [
        fieldname for fieldname in SCHOLARSHIP_REGISTRATION_REQUIRED_FIELDS if not registration_doc.get(fieldname)
    ]
    if missing:
        labels = [_(registration_doc.meta.get_label(fieldname)) for fieldname in missing]
        frappe.throw(
            _("The registration is incomplete. Missing: {0}").format(", ".join(labels)),
            IncompleteScholarshipApplicationError,
        )


def new_scholarship_request(request: dict) -> Document:
    request_doc = frappe.new_doc("Beneficiary Request")
    request_doc.update({fieldname: request.get(fieldname) for fieldname in REQUEST_INPUT_FIELDS})
    request_doc.update(
        {
            "request_category": "Education Assistance",
            "educational_assistance": "Scholarship",
            "is_scholarship": 1,
        }
    )
    request_doc.flags.is_scholarship_submission = True
    return request_doc


def get_own_unattached_files(request: dict) -> dict[str, str | None]:
    """Map each File the request points at to its attachment field, or None for an other attachment.

    Only Files the session user uploaded and has not attached yet are accepted, so a user cannot point
    their request at somebody else's documents. It runs before the request is inserted, so a refused
    file creates nothing.
    """
    meta = frappe.get_meta("Beneficiary Request")
    wanted = [
        (fieldname, request.get(fieldname), _(meta.get_label(fieldname)))
        for fieldname in SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS
    ]
    wanted += [(None, file_url, _("Other Attachments")) for file_url in request.get("other_attachments") or []]

    files = {}
    for fieldname, file_url, label in wanted:
        filters = {"file_url": file_url, "owner": frappe.session.user, "attached_to_name": ("is", "not set")}
        # The same file_url sent twice must not resolve to the same File twice.
        if files:
            filters["name"] = ("not in", list(files))

        file_name = file_url and frappe.db.get_value("File", filters, "name")
        if not file_name:
            raise frappe.PermissionError(
                _("The file for {0} was not uploaded by you or is already in use.").format(label)
            )
        files[file_name] = fieldname
    return files


def attach_files_to_request(request_files: dict[str, str | None], request_doc: Document) -> None:
    """Attach the Files found by get_own_unattached_files to the inserted request.

    Frappe's attach_files_to_document hook may already have linked some of them to this request by
    file_url while it was inserted; they are set again here so each File gets its own field.
    """
    for file_name, fieldname in request_files.items():
        file_doc = frappe.get_doc("File", file_name)
        file_doc.update(
            {
                "attached_to_doctype": request_doc.doctype,
                "attached_to_name": request_doc.name,
                "attached_to_field": fieldname,
            }
        )
        file_doc.save(ignore_permissions=True)
