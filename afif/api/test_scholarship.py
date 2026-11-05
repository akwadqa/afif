import random
from io import BytesIO
from unittest.mock import patch

import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests import IntegrationTestCase
from frappe.utils import random_string
from pypdf import PdfWriter

from afif.afif.doctype.beneficiaries_registration.beneficiaries_registration import (
    ScholarshipFlagChangeError as RegistrationFlagChangeError,
)
from afif.afif.doctype.beneficiaries_registration.beneficiaries_registration import (
    ScholarshipMaritalStatusError,
    ScholarshipSubmissionError,
    SingleMaritalStatusError,
)
from afif.afif.doctype.beneficiary_request.beneficiary_request import (
    SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS,
    IncompleteScholarshipRequestError,
    ScholarshipSubcategoryError,
)
from afif.afif.doctype.beneficiary_request.beneficiary_request import (
    ScholarshipFlagChangeError as RequestFlagChangeError,
)
from afif.api.scholarship import IncompleteScholarshipApplicationError, submit_scholarship_application
from afif.hooks_call import get_marital_status, get_missing_required_attachments, is_registration_complete

REGISTRATION_ATTACHMENTS = {
    "qid": "/files/test-qid.pdf",
    "passport": "/files/test-passport.pdf",
    "metrash_adress": "/files/test-metrash.pdf",
    "employment_certificate": "/files/test-employment.pdf",
    # visa_type defaults to Residence, which requires these as well.
    "bank_statement": "/files/test-bank-statement.pdf",
    "beneficiary_credit_certificate": "/files/test-credit.pdf",
    "vehicle_certificate": "/files/test-vehicle.pdf",
    "iban_picture": "/files/test-iban.pdf",
}
REQUEST_FILE_TARGETS = ("student_id_copy", "other_attachments")


class TestSubmitScholarshipApplication(IntegrationTestCase):
    def setUp(self):
        sanadi = patch("afif.hooks_call.requests.post", side_effect=AssertionError("Sanadi must not be called"))
        sanadi.start()
        self.addCleanup(sanadi.stop)
        self.addCleanup(frappe.set_user, "Administrator")

        self.user = make_beneficiary_user()
        frappe.set_user(self.user)
        self.registration = make_registration(is_scholarship=1)
        self.request_data = make_request_data()

    def test_submit_creates_request_and_submits_registration(self):
        submit_scholarship_application(self.registration, self.request_data)

        registration = frappe.get_doc("Beneficiaries Registration", self.registration)
        self.assertEqual(registration.workflow_state, "New Registration")
        self.assertEqual(registration.status, "New Registration")

        request = frappe.get_doc("Beneficiary Request", frappe.response["data"]["request"])
        self.assertEqual(request.beneficiaries, self.registration)
        self.assertEqual(request.workflow_state, "Pending Supervisor Approval")
        self.assertEqual(request.request_category, "Education Assistance")
        self.assertEqual(request.educational_assistance, "Scholarship")
        self.assertEqual(request.is_scholarship, 1)
        self.assertTrue(request.request_date)

    def test_submit_attaches_the_documents_to_the_request(self):
        submit_scholarship_application(self.registration, self.request_data)

        assert_documents_attached_to_request(self, frappe.response["data"]["request"], self.request_data)

    def test_submit_without_registration_documents_succeeds(self):
        registration = frappe.get_doc("Beneficiaries Registration", self.registration)
        attach_fields = registration.meta.get("fields", {"fieldtype": ("in", ("Attach", "Attach Image"))})
        uploaded = [df.fieldname for df in attach_fields if (registration.get(df.fieldname) or "").startswith("/")]
        self.assertEqual(uploaded, [])

        submit_scholarship_application(self.registration, self.request_data)

        self.assertEqual(registration.reload().workflow_state, "New Registration")

    def test_applicant_can_read_only_their_own_request(self):
        submit_scholarship_application(self.registration, self.request_data)
        request = frappe.response["data"]["request"]

        self.assertTrue(frappe.has_permission("Beneficiary Request", "read", request))
        frappe.set_user("Administrator")
        frappe.set_user(make_beneficiary_user())
        self.assertFalse(frappe.has_permission("Beneficiary Request", "read", request))

    def test_missing_request_document_creates_nothing(self):
        for fieldname in SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS:
            with self.subTest(fieldname), self.assertRaises(IncompleteScholarshipRequestError):
                submit_scholarship_application(self.registration, {**self.request_data, fieldname: None})

        self.assert_nothing_submitted()
        assert_files_unattached(self, self.request_data)

    def test_another_users_file_is_rejected(self):
        frappe.set_user("Administrator")
        frappe.set_user(make_beneficiary_user())
        other_file_url = upload_unattached_file("other-user")
        frappe.set_user(self.user)

        for target in REQUEST_FILE_TARGETS:
            with self.subTest(target), self.assertRaises(frappe.PermissionError):
                submit_scholarship_application(self.registration, replace_file(self.request_data, target, other_file_url))

        self.assert_nothing_submitted()

    def test_a_file_already_attached_elsewhere_is_rejected(self):
        for target in REQUEST_FILE_TARGETS:
            request_data = make_request_data()
            attached_url = upload_unattached_file("attached-elsewhere")
            attach_file_to(attached_url, "Beneficiaries Registration", self.registration)

            with self.subTest(target), self.assertRaises(frappe.PermissionError):
                submit_scholarship_application(self.registration, replace_file(request_data, target, attached_url))

        self.assert_nothing_submitted()

    def test_a_public_file_is_rejected(self):
        public_file_url = upload_unattached_file("public", is_private=0)

        with self.assertRaises(frappe.PermissionError):
            submit_scholarship_application(self.registration, {**self.request_data, "student_id_copy": public_file_url})

        self.assert_nothing_submitted()

    def test_other_attachments_must_be_a_list(self):
        request_data = {**self.request_data, "other_attachments": self.request_data["other_attachments"][0]}

        with self.assertRaises(frappe.ValidationError):
            submit_scholarship_application(self.registration, request_data)

        self.assert_nothing_submitted()

    def test_the_same_file_for_two_documents_is_rejected(self):
        request_data = {**self.request_data, "student_passport_copy": self.request_data["student_id_copy"]}

        with self.assertRaises(frappe.PermissionError):
            submit_scholarship_application(self.registration, request_data)

        self.assert_nothing_submitted()

    def test_missing_registration_consent_creates_nothing(self):
        frappe.db.set_value("Beneficiaries Registration", self.registration, "verification_consent", 0)

        with self.assertRaises(IncompleteScholarshipApplicationError):
            submit_scholarship_application(self.registration, self.request_data)

        self.assert_nothing_submitted()

    def test_missing_passport_number_creates_nothing(self):
        frappe.db.set_value("Beneficiaries Registration", self.registration, "passport_number", None)

        with self.assertRaises(IncompleteScholarshipApplicationError):
            submit_scholarship_application(self.registration, self.request_data)

        self.assert_nothing_submitted()

    def test_missing_guardian_mobile_number_creates_nothing(self):
        frappe.db.set_value("Beneficiaries Registration", self.registration, "guardian_mobile_number", None)

        with self.assertRaises(IncompleteScholarshipApplicationError):
            submit_scholarship_application(self.registration, self.request_data)

        self.assert_nothing_submitted()

    def test_older_draft_that_is_not_single_cannot_be_submitted(self):
        frappe.db.set_value("Beneficiaries Registration", self.registration, "marital_status", "Separated")

        with self.assertRaises(ScholarshipMaritalStatusError):
            submit_scholarship_application(self.registration, self.request_data)

        self.assert_nothing_submitted()

    def test_missing_request_data_creates_nothing(self):
        cases = {
            "missing amount": {"requested_amount": None},
            "zero amount": {"requested_amount": "0"},
            "missing summary": {"request_summary": None},
            "blank summary": {"request_summary": "   "},
            "unchecked declaration": {"is_eligibility_check_accepted": 0},
        }
        for case, override in cases.items():
            with self.subTest(case), self.assertRaises(IncompleteScholarshipRequestError):
                submit_scholarship_application(self.registration, {**self.request_data, **override})

        self.assert_nothing_submitted()

    def test_rejects_another_users_registration(self):
        frappe.set_user("Administrator")
        other_user = make_beneficiary_user()
        frappe.set_user(other_user)
        other_registration = make_registration(is_scholarship=1)
        frappe.set_user(self.user)

        with self.assertRaises(frappe.PermissionError):
            submit_scholarship_application(other_registration, self.request_data)

        self.assertEqual(
            frappe.db.get_value("Beneficiaries Registration", other_registration, "workflow_state"), "Draft"
        )

    def test_already_submitted_application_cannot_be_resubmitted(self):
        submit_scholarship_application(self.registration, self.request_data)

        with self.assertRaises(frappe.ValidationError):
            submit_scholarship_application(self.registration, make_request_data())

        self.assertEqual(frappe.db.count("Beneficiary Request", {"beneficiaries": self.registration}), 1)

    def test_registration_flag_cannot_change(self):
        registration = frappe.get_doc("Beneficiaries Registration", self.registration)
        registration.is_scholarship = 0

        with self.assertRaises(RegistrationFlagChangeError):
            registration.save()

    def test_request_flag_cannot_change(self):
        submit_scholarship_application(self.registration, self.request_data)
        frappe.set_user("Administrator")
        request = frappe.get_doc("Beneficiary Request", frappe.response["data"]["request"])
        request.is_scholarship = 0

        with self.assertRaises(RequestFlagChangeError):
            request.save()

    def test_scholarship_registration_cannot_be_submitted_without_its_request(self):
        registration = frappe.get_doc("Beneficiaries Registration", self.registration)

        with self.assertRaises(ScholarshipSubmissionError):
            apply_workflow(registration, "Submit")

    def test_plain_insert_of_scholarship_request_is_blocked_for_non_accepted_user(self):
        request = make_plain_scholarship_request(self.registration, self.request_data)

        with self.assertRaises(frappe.PermissionError):
            request.insert()

    def test_plain_insert_of_scholarship_request_is_blocked_for_accepted_user(self):
        accept_registration(self.registration, self.user)
        cases = {
            "with the flag": (1, RequestFlagChangeError),
            "without the flag": (0, ScholarshipSubcategoryError),
        }
        for case, (is_scholarship, error) in cases.items():
            request = make_plain_scholarship_request(self.registration, self.request_data)
            request.is_scholarship = is_scholarship
            with self.subTest(case), self.assertRaises(error):
                request.insert()

        self.assertFalse(frappe.db.exists("Beneficiary Request", {"beneficiaries": self.registration}))

    def test_request_cannot_be_switched_to_or_from_scholarship(self):
        submit_scholarship_application(self.registration, self.request_data)
        scholarship_request = frappe.response["data"]["request"]
        frappe.set_user("Administrator")
        other_user = make_beneficiary_user()
        frappe.set_user(other_user)
        accept_registration(make_registration(is_scholarship=0), other_user)
        normal_request = make_normal_education_request()
        frappe.set_user("Administrator")

        cases = {
            "normal request to Scholarship": (normal_request, "Scholarship"),
            "scholarship request to Tuition Fees": (scholarship_request, "Tuition Fees"),
        }
        for case, (name, subcategory) in cases.items():
            request = frappe.get_doc("Beneficiary Request", name)
            request.educational_assistance = subcategory
            with self.subTest(case), self.assertRaises(ScholarshipSubcategoryError):
                request.save()

    def assert_nothing_submitted(self):
        self.assertEqual(
            frappe.db.get_value("Beneficiaries Registration", self.registration, "workflow_state"), "Draft"
        )
        self.assertFalse(frappe.db.exists("Beneficiary Request", {"beneficiaries": self.registration}))


class TestSingleMaritalStatus(IntegrationTestCase):
    def setUp(self):
        self.addCleanup(frappe.set_user, "Administrator")
        self.user = make_beneficiary_user()
        frappe.set_user(self.user)

    def test_scholarship_applicant_can_be_single_and_is_sent_to_sanadi_as_single(self):
        registration = frappe.get_doc("Beneficiaries Registration", make_registration(is_scholarship=1))
        registration.marital_status = "Single"
        registration.save()

        self.assertEqual(get_marital_status(registration.reload()), 1)

    def test_scholarship_registration_accepts_single(self):
        registration = frappe.get_doc("Beneficiaries Registration", make_registration(is_scholarship=1))

        self.assertEqual(registration.marital_status, "Single")

    def test_scholarship_registration_refuses_married(self):
        name = make_registration(is_scholarship=1)

        for marital_status in ("Married", "Divorced", "Widowed", "Separated"):
            with self.subTest(marital_status):
                with self.assertRaises(ScholarshipMaritalStatusError):
                    make_registration(is_scholarship=1, marital_status=marital_status)

                registration = frappe.get_doc("Beneficiaries Registration", name)
                registration.marital_status = marital_status
                with self.assertRaises(ScholarshipMaritalStatusError):
                    registration.save()

    def test_older_married_scholarship_registration_can_still_be_saved(self):
        name = make_registration(is_scholarship=1)
        frappe.db.set_value("Beneficiaries Registration", name, "marital_status", "Married")
        registration = frappe.get_doc("Beneficiaries Registration", name)
        registration.en_name = "Older Married Scholarship Registration"

        registration.save()

        self.assertEqual(registration.reload().marital_status, "Married")

    def test_normal_registration_still_refuses_single(self):
        registration = frappe.get_doc("Beneficiaries Registration", make_registration(is_scholarship=0))
        registration.marital_status = "Single"

        with self.assertRaises(SingleMaritalStatusError):
            registration.save()

    def test_older_single_registration_can_still_be_saved(self):
        name = make_registration(is_scholarship=0)
        frappe.db.set_value("Beneficiaries Registration", name, "marital_status", "Single")
        registration = frappe.get_doc("Beneficiaries Registration", name)
        registration.en_name = "Older Single Registration"

        registration.save()

        self.assertEqual(registration.reload().marital_status, "Single")


class TestScholarshipRegistrationAttachments(IntegrationTestCase):
    def setUp(self):
        self.addCleanup(frappe.set_user, "Administrator")
        frappe.set_user(make_beneficiary_user())

    def test_scholarship_registration_needs_no_attachments(self):
        registration = frappe.get_doc("Beneficiaries Registration", make_registration(is_scholarship=1))

        self.assertEqual(get_missing_required_attachments(registration), [])
        self.assertTrue(is_registration_complete(registration))

    def test_normal_registration_attachment_rules_unchanged(self):
        registration = frappe.get_doc("Beneficiaries Registration", make_registration(is_scholarship=0))
        self.assertEqual(get_missing_required_attachments(registration), [])

        registration.qid = None
        registration.marital_status = "Married"
        self.assertEqual(get_missing_required_attachments(registration), ["qid", "wife_id", "wife_passport"])
        self.assertFalse(is_registration_complete(registration))


class TestNormalFlowUnchanged(IntegrationTestCase):
    def setUp(self):
        sanadi = patch("afif.hooks_call.requests.post", side_effect=AssertionError("Sanadi must not be called"))
        sanadi.start()
        self.addCleanup(sanadi.stop)
        self.addCleanup(frappe.set_user, "Administrator")

        self.user = make_beneficiary_user()
        frappe.set_user(self.user)

    def test_normal_registration_submits_through_the_workflow(self):
        registration = frappe.get_doc("Beneficiaries Registration", make_registration(is_scholarship=0))

        apply_workflow(registration, "Submit")

        self.assertEqual(registration.reload().workflow_state, "New Registration")
        self.assertEqual(registration.is_scholarship, 0)

    def test_accepted_user_creates_a_normal_education_request(self):
        registration = make_registration(is_scholarship=0)
        accept_registration(registration, self.user)

        request = frappe.get_doc("Beneficiary Request", make_normal_education_request())

        self.assertEqual(request.beneficiaries, registration)
        self.assertEqual(request.workflow_state, "Pending Supervisor Approval")
        self.assertEqual(request.is_scholarship, 0)


def make_beneficiary_user() -> str:
    email = f"scholarship-test-{random_string(8).lower()}@example.com"
    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": "Scholarship Test",
            "user_type": "Website User",
            "send_welcome_email": 0,
            # Same profile and role a real signup ends up with.
            "role_profiles": [{"role_profile": "Beneficiary New Registration"}],
        }
    ).insert(ignore_permissions=True)
    return user.name


def accept_registration(registration: str, user: str) -> None:
    """Reach the state create_new_beneficiary leaves behind, without calling Sanadi."""
    frappe.db.set_value("Beneficiaries Registration", registration, {"workflow_state": "Accepted", "status": "Accepted"})
    frappe.set_user("Administrator")
    user_doc = frappe.get_doc("User", user)
    user_doc.role_profiles = []
    user_doc.append("role_profiles", {"role_profile": "Beneficiary Accepted"})
    user_doc.save(ignore_permissions=True)
    frappe.set_user(user)


def make_registration(is_scholarship: int, **fields) -> str:
    registration = frappe.get_doc(
        {
            "doctype": "Beneficiaries Registration",
            "is_scholarship": is_scholarship,
            "en_name": "Scholarship Test",
            "ar_name": "اختبار المنحة",
            "email": frappe.session.user,
            "ben_primary_idtype": "Qatari Id",
            "ben_primary_idnumber": str(random.randint(10**10, 10**11 - 1)),
            "passport_number": "A1234567",
            # Single is for scholarship applicants only, and the only status they may hold.
            "marital_status": "Single" if is_scholarship else "Separated",
            "currently_working": "Yes",
            "documents_confirmation": 1,
            "verification_consent": 1,
            "cancellation_right": 1,
            "guardian_mobile_number": "55123456" if is_scholarship else None,
            "current_step": 5,
            # A scholarship applicant uploads their documents with the request, not the registration.
            **({} if is_scholarship else REGISTRATION_ATTACHMENTS),
            **fields,
        }
    ).insert()
    return registration.name


def make_request_data() -> dict:
    return {
        "requested_amount": "15000",
        "request_summary": "Scholarship test request",
        "is_data_accuracy_declared": 1,
        "is_eligibility_check_accepted": 1,
        **{fieldname: upload_unattached_file(fieldname) for fieldname in SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS},
        "other_attachments": [upload_unattached_file("other-attachment")],
    }


def replace_file(request_data: dict, target: str, file_url: str) -> dict:
    """Point one of the request's files, a named document or the extra file, at another file_url."""
    if target == "other_attachments":
        return {**request_data, "other_attachments": [file_url]}
    return {**request_data, target: file_url}


def attach_file_to(file_url: str, doctype: str, name: str) -> None:
    file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
    frappe.db.set_value("File", file_name, {"attached_to_doctype": doctype, "attached_to_name": name})


def assert_documents_attached_to_request(testcase: IntegrationTestCase, request: str, request_data: dict) -> None:
    request_doc = frappe.get_doc("Beneficiary Request", request)
    expected = [(fieldname, request_data[fieldname]) for fieldname in SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS]
    expected += [(None, file_url) for file_url in request_data["other_attachments"]]

    for fieldname, file_url in expected:
        if fieldname:
            testcase.assertEqual(request_doc.get(fieldname), file_url)
        file = frappe.db.get_value(
            "File",
            {"file_url": file_url},
            ["attached_to_doctype", "attached_to_name", "attached_to_field", "is_private"],
            as_dict=True,
        )
        testcase.assertEqual(
            (file.attached_to_doctype, file.attached_to_name, file.attached_to_field or None, file.is_private),
            ("Beneficiary Request", request, fieldname, 1),
        )


def assert_files_unattached(testcase: IntegrationTestCase, request_data: dict) -> None:
    file_urls = [request_data[fieldname] for fieldname in SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS]
    file_urls += request_data["other_attachments"]
    attached = frappe.get_all(
        "File", filters={"file_url": ("in", file_urls), "attached_to_name": ("is", "set")}, pluck="file_url"
    )
    testcase.assertEqual(attached, [])


def make_normal_education_request() -> str:
    return frappe.get_doc(make_normal_education_request_data()).insert().name


def make_normal_education_request_data() -> dict:
    return {
        "doctype": "Beneficiary Request",
        "request_category": "Education Assistance",
        "educational_assistance": "Tuition Fees",
        "requested_amount": "1000",
        "request_summary": "Tuition fees",
        "education_invoice": upload_unattached_file("education_invoice"),
        "grade_transcript": upload_unattached_file("grade_transcript"),
    }


def upload_unattached_file(label: str, is_private: int = 1) -> str:
    file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": f"{label}.pdf",
            "content": make_pdf(),
            "is_private": is_private,
        }
    ).insert()
    return file.file_url


def make_pdf() -> bytes:
    # Unique metadata keeps Frappe from deduplicating uploads into one shared file_url.
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata({"/Title": random_string(16)})
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def make_plain_scholarship_request(registration: str, request_data: dict):
    return frappe.get_doc(
        {
            "doctype": "Beneficiary Request",
            "request_category": "Education Assistance",
            "educational_assistance": "Scholarship",
            "is_scholarship": 1,
            "beneficiaries": registration,
            **request_data,
        }
    )
