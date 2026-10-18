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
from afif.afif.doctype.beneficiaries_registration.beneficiaries_registration import ScholarshipSubmissionError
from afif.afif.doctype.beneficiary_request.beneficiary_request import (
    SCHOLARSHIP_ATTACHMENT_FIELDS,
    IncompleteScholarshipRequestError,
)
from afif.afif.doctype.beneficiary_request.beneficiary_request import (
    ScholarshipFlagChangeError as RequestFlagChangeError,
)
from afif.api.scholarship import IncompleteScholarshipApplicationError, submit_scholarship_application

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

        for fieldname in SCHOLARSHIP_ATTACHMENT_FIELDS:
            attached = frappe.db.get_value(
                "File",
                {"file_url": request.get(fieldname), "owner": self.user},
                ["attached_to_doctype", "attached_to_name", "attached_to_field"],
                as_dict=True,
            )
            self.assertEqual(
                (attached.attached_to_doctype, attached.attached_to_name, attached.attached_to_field),
                ("Beneficiary Request", request.name, fieldname),
            )

    def test_missing_registration_attachment_creates_nothing(self):
        frappe.db.set_value("Beneficiaries Registration", self.registration, "qid", None)

        with self.assertRaises(IncompleteScholarshipApplicationError):
            submit_scholarship_application(self.registration, self.request_data)

        self.assert_nothing_submitted()

    def test_missing_registration_consent_creates_nothing(self):
        frappe.db.set_value("Beneficiaries Registration", self.registration, "verification_consent", 0)

        with self.assertRaises(IncompleteScholarshipApplicationError):
            submit_scholarship_application(self.registration, self.request_data)

        self.assert_nothing_submitted()

    def test_missing_request_data_creates_nothing(self):
        cases = {
            "missing attachment": {"scholarship_student_passport": None},
            "reused existing attachment field": {"grade_transcript": None},
            "missing amount": {"requested_amount": None},
            "zero amount": {"requested_amount": "0"},
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

    def test_rejects_another_users_file(self):
        frappe.set_user("Administrator")
        other_user = make_beneficiary_user()
        frappe.set_user(other_user)
        other_file_url = upload_unattached_file("other-user")
        frappe.set_user(self.user)

        with self.assertRaises(frappe.PermissionError):
            submit_scholarship_application(
                self.registration, {**self.request_data, "scholarship_family_ids": other_file_url}
            )

        self.assert_nothing_submitted()

    def test_rejects_a_file_already_attached_elsewhere(self):
        file_url = self.request_data["scholarship_family_ids"]
        file_name = frappe.db.get_value("File", {"file_url": file_url}, "name")
        frappe.db.set_value(
            "File",
            file_name,
            {"attached_to_doctype": "Beneficiaries Registration", "attached_to_name": self.registration},
        )

        with self.assertRaises(frappe.PermissionError):
            submit_scholarship_application(self.registration, self.request_data)

        self.assert_nothing_submitted()

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
        request = make_plain_scholarship_request(self.registration, self.request_data)

        with self.assertRaises(RequestFlagChangeError):
            request.insert()

    def assert_nothing_submitted(self):
        self.assertEqual(
            frappe.db.get_value("Beneficiaries Registration", self.registration, "workflow_state"), "Draft"
        )
        self.assertFalse(frappe.db.exists("Beneficiary Request", {"beneficiaries": self.registration}))


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

        request = frappe.get_doc(
            {
                "doctype": "Beneficiary Request",
                "request_category": "Education Assistance",
                "educational_assistance": "Tuition Fees",
                "requested_amount": "1000",
                "request_summary": "Tuition fees",
            }
        ).insert()

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


def make_registration(is_scholarship: int) -> str:
    registration = frappe.get_doc(
        {
            "doctype": "Beneficiaries Registration",
            "is_scholarship": is_scholarship,
            "en_name": "Scholarship Test",
            "ar_name": "اختبار المنحة",
            "email": frappe.session.user,
            "ben_primary_idtype": "Qatari Id",
            "ben_primary_idnumber": str(random.randint(10**10, 10**11 - 1)),
            "marital_status": "Separated",
            "currently_working": "Yes",
            "documents_confirmation": 1,
            "verification_consent": 1,
            "cancellation_right": 1,
            "current_step": 5,
            **REGISTRATION_ATTACHMENTS,
        }
    ).insert()
    return registration.name


def make_request_data() -> dict:
    return {
        "requested_amount": "15000",
        "request_summary": "Scholarship test request",
        "is_data_accuracy_declared": 1,
        "is_eligibility_check_accepted": 1,
        **{fieldname: upload_unattached_file(fieldname) for fieldname in SCHOLARSHIP_ATTACHMENT_FIELDS},
    }


def upload_unattached_file(label: str) -> str:
    file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": f"{label}.pdf",
            "content": make_pdf(),
            "is_private": 1,
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
