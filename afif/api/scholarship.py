import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.workflow import apply_workflow

from afif.afif.doctype.beneficiaries_registration.beneficiaries_registration import SCHOLARSHIP_ATTACHMENT_FIELDS
from afif.afif.doctype.beneficiary_request.beneficiary_request import SCHOLARSHIP_DECLARATION_FIELDS
from afif.api.response import gen_response
from afif.hooks_call import get_missing_required_attachments

REGISTRATION_CONSENT_FIELDS = ("documents_confirmation", "verification_consent", "cancellation_right")
SCHOLARSHIP_REGISTRATION_REQUIRED_FIELDS = (
    "passport_number",
    "guardian_mobile_number",
    *REGISTRATION_CONSENT_FIELDS,
    *SCHOLARSHIP_ATTACHMENT_FIELDS,
)
REQUEST_INPUT_FIELDS = ("requested_amount", "request_summary", *SCHOLARSHIP_DECLARATION_FIELDS)


class IncompleteScholarshipApplicationError(frappe.ValidationError):
    pass


@frappe.whitelist(methods=["POST"])
def submit_scholarship_application(registration: str, request: dict | str) -> None:
    """Submit a scholarship Draft registration and create its Beneficiary Request in one transaction.

    The scholarship documents were already uploaded and saved on the Draft, step by step.
    """
    registration_doc = get_own_scholarship_draft(registration)
    validate_registration_complete(registration_doc)

    request_doc = new_scholarship_request(frappe.parse_json(request))
    request_doc.beneficiaries = registration_doc.name
    # The registration is submitted in this same transaction, so it is not Accepted yet.
    request_doc.flags.is_new_scholarship_applicant = True
    request_doc.validate_scholarship_request()

    # Everything is validated before the first write, so a failure leaves both documents untouched.
    registration_doc.flags.is_scholarship_submission = True
    apply_workflow(registration_doc, "Submit")
    # Not-yet-accepted beneficiaries have no create permission on requests; ownership of the
    # registration was checked above.
    request_doc.insert(ignore_permissions=True)

    gen_response(
        200,
        _("Scholarship application submitted"),
        {"registration": registration_doc.name, "request": request_doc.name},
    )


@frappe.whitelist(methods=["POST"])
def create_scholarship_request(request: dict | str) -> None:
    """Create a new scholarship request for an accepted scholarship beneficiary, and put its documents
    on their registration.

    Only a Supervisor may save an Accepted registration, so the files are uploaded unattached and the
    endpoint writes them onto the registration once the request is allowed.
    """
    # The scholarship is its own flow: a beneficiary who registered through the normal flow cannot
    # apply for it (plan Phase 7).
    if not frappe.db.get_value("Beneficiaries Registration", {"user": frappe.session.user}, "is_scholarship"):
        raise frappe.PermissionError(_("Only scholarship applicants can file a scholarship request."))

    request = frappe.parse_json(request)
    request_doc = new_scholarship_request(request)
    request_doc.validate_scholarship_request()
    validate_scholarship_attachments_given(request)
    registration_files = get_unattached_own_files(request)

    # Normal permissions and before_insert_request apply: accepted beneficiaries only, and the
    # pending-request and cooldown rules (OQ5). before_insert_request sets the registration.
    request_doc.insert()
    attach_files_to_registration(registration_files, request_doc.beneficiaries)

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
    missing = get_missing_required_attachments(registration_doc)
    missing += [
        fieldname for fieldname in SCHOLARSHIP_REGISTRATION_REQUIRED_FIELDS if not registration_doc.get(fieldname)
    ]
    if missing:
        labels = [_(registration_doc.meta.get_label(fieldname)) for fieldname in missing]
        frappe.throw(
            _("The registration is incomplete. Missing: {0}").format(", ".join(labels)),
            IncompleteScholarshipApplicationError,
        )


def validate_scholarship_attachments_given(request: dict) -> None:
    missing = [fieldname for fieldname in SCHOLARSHIP_ATTACHMENT_FIELDS if not request.get(fieldname)]
    if missing:
        meta = frappe.get_meta("Beneficiaries Registration")
        frappe.throw(
            _("The scholarship request is incomplete. Missing: {0}").format(
                ", ".join(_(meta.get_label(fieldname)) for fieldname in missing)
            ),
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


def get_unattached_own_files(request: dict) -> dict[str, str]:
    """Map each scholarship attachment field to a File the session user uploaded and has not attached yet.

    Without this check a user could point their registration at somebody else's uploaded documents.
    """
    files = {}
    for fieldname in SCHOLARSHIP_ATTACHMENT_FIELDS:
        filters = {
            "file_url": request.get(fieldname),
            "owner": frappe.session.user,
            "attached_to_name": ("is", "not set"),
        }
        if files:
            filters["name"] = ("not in", list(files.values()))

        file_name = frappe.db.get_value("File", filters, "name")
        if not file_name:
            raise frappe.PermissionError(
                _("The file for {0} was not uploaded by you or is already in use.").format(
                    _(frappe.get_meta("Beneficiaries Registration").get_label(fieldname))
                )
            )
        files[fieldname] = file_name
    return files


def attach_files_to_registration(registration_files: dict[str, str], registration: str) -> None:
    file_urls = {}
    for fieldname, file_name in registration_files.items():
        file_doc = frappe.get_doc("File", file_name)
        file_doc.update(
            {
                "attached_to_doctype": "Beneficiaries Registration",
                "attached_to_name": registration,
                "attached_to_field": fieldname,
            }
        )
        file_doc.save(ignore_permissions=True)
        file_urls[fieldname] = file_doc.file_url

    # Written without saving the registration: saving an Accepted one re-runs create_new_beneficiary,
    # which registers the beneficiary in Sanadi again and resets the acceptance date.
    # The previous scholarship's documents stay attached, as the record of that request.
    frappe.db.set_value("Beneficiaries Registration", registration, file_urls)
