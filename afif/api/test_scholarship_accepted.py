from datetime import timedelta
from unittest.mock import patch

import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests import IntegrationTestCase
from frappe.utils import add_months, now_datetime

from afif.afif.doctype.beneficiaries_registration.beneficiaries_registration import SCHOLARSHIP_ATTACHMENT_FIELDS
from afif.afif.doctype.beneficiary_request.beneficiary_request import IncompleteScholarshipRequestError
from afif.api.scholarship import IncompleteScholarshipApplicationError, create_scholarship_request
from afif.api.test_scholarship import (
    accept_registration,
    make_beneficiary_user,
    make_registration,
    make_request_data,
    upload_unattached_file,
)
from afif.api.test_scholarship_decision import ScholarshipDecisionTestCase, upload_declaration


class AcceptedBeneficiaryTestCase(IntegrationTestCase):
    def setUp(self):
        sanadi = patch("afif.hooks_call.requests.post", side_effect=AssertionError("Sanadi must not be called"))
        sanadi.start()
        self.addCleanup(sanadi.stop)
        self.addCleanup(frappe.set_user, "Administrator")

        self.user = make_beneficiary_user()
        frappe.set_user(self.user)
        self.registration = make_registration(is_scholarship=0)
        accept_registration(self.registration, self.user)

    def create_request(self, request_data: dict | None = None) -> str:
        create_scholarship_request(request_data or make_accepted_request_data())
        return frappe.response["data"]["request"]

    def get_request_count(self) -> int:
        return frappe.db.count("Beneficiary Request", {"beneficiaries": self.registration})


class TestAcceptedBeneficiaryScholarshipRequest(AcceptedBeneficiaryTestCase):
    def test_accepted_user_creates_a_scholarship_request_with_its_files_on_the_registration(self):
        request_data = make_accepted_request_data()
        request = frappe.get_doc("Beneficiary Request", self.create_request(request_data))

        self.assertEqual(request.beneficiaries, self.registration)
        self.assertEqual(
            (request.request_category, request.educational_assistance),
            ("Education Assistance", "Scholarship"),
        )
        self.assertEqual(request.workflow_state, "Pending Supervisor Approval")
        self.assertEqual(request.is_scholarship, 1)
        self.assertTrue(request.request_date)

        registration = frappe.get_doc("Beneficiaries Registration", self.registration)
        self.assertEqual(registration.workflow_state, "Accepted")
        for fieldname in SCHOLARSHIP_ATTACHMENT_FIELDS:
            self.assertEqual(registration.get(fieldname), request_data[fieldname])
            attached = frappe.db.get_value(
                "File",
                {"file_url": request_data[fieldname], "owner": self.user},
                ["attached_to_doctype", "attached_to_name", "attached_to_field", "is_private"],
                as_dict=True,
            )
            self.assertEqual(
                (attached.attached_to_doctype, attached.attached_to_name, attached.attached_to_field),
                ("Beneficiaries Registration", self.registration, fieldname),
            )
            self.assertEqual(attached.is_private, 1)

    def test_incomplete_request_creates_nothing(self):
        cases = {
            "missing attachment": ({"scholarship_guardian_bank_statement": None}, IncompleteScholarshipApplicationError),
            "missing invoice": ({"scholarship_university_invoice": None}, IncompleteScholarshipApplicationError),
            "missing amount": ({"requested_amount": None}, IncompleteScholarshipRequestError),
            "missing summary": ({"request_summary": ""}, IncompleteScholarshipRequestError),
            "unchecked declaration": ({"is_data_accuracy_declared": 0}, IncompleteScholarshipRequestError),
        }
        for case, (override, error) in cases.items():
            with self.subTest(case), self.assertRaises(error):
                self.create_request({**make_accepted_request_data(), **override})

        self.assertEqual(self.get_request_count(), 0)
        self.assertFalse(frappe.db.get_value("Beneficiaries Registration", self.registration, "scholarship_student_id"))

    def test_another_users_file_is_rejected(self):
        frappe.set_user("Administrator")
        frappe.set_user(make_beneficiary_user())
        other_file_url = upload_unattached_file("other-user")
        frappe.set_user(self.user)

        with self.assertRaises(frappe.PermissionError):
            self.create_request({**make_accepted_request_data(), "scholarship_student_id": other_file_url})

        self.assertEqual(self.get_request_count(), 0)
        self.assertFalse(frappe.db.get_value("Beneficiaries Registration", self.registration, "scholarship_student_id"))

    def test_a_file_already_attached_elsewhere_is_rejected(self):
        request_data = make_accepted_request_data()
        file_name = frappe.db.get_value("File", {"file_url": request_data["scholarship_grade_transcript"]}, "name")
        frappe.db.set_value(
            "File",
            file_name,
            {"attached_to_doctype": "Beneficiaries Registration", "attached_to_name": self.registration},
        )

        with self.assertRaises(frappe.PermissionError):
            self.create_request(request_data)

        self.assertEqual(self.get_request_count(), 0)

    def test_not_accepted_user_cannot_create_a_scholarship_request(self):
        frappe.set_user("Administrator")
        user = make_beneficiary_user()
        frappe.set_user(user)
        registration = make_registration(is_scholarship=0)

        with self.assertRaises(frappe.PermissionError):
            self.create_request()

        self.assertFalse(frappe.db.exists("Beneficiary Request", {"beneficiaries": registration}))


class TestScholarshipRequestCooldowns(AcceptedBeneficiaryTestCase):
    """The normal request rules apply to scholarship requests (OQ5)."""

    def test_pending_request_blocks_a_scholarship_request(self):
        self.make_previous_request()

        with self.assertRaisesRegex(frappe.ValidationError, "pending review"):
            self.create_request()

        self.assertEqual(self.get_request_count(), 1)

    def test_recent_rejection_blocks_a_scholarship_request(self):
        self.close_request(self.make_previous_request(), "Rejected", rejected_date=add_months(now_datetime(), -2))

        with self.assertRaisesRegex(frappe.ValidationError, "Three months"):
            self.create_request()

    def test_recent_approval_blocks_a_scholarship_request(self):
        self.close_request(
            self.make_previous_request(), "Approved For Aid", approved_for_aid_date=add_months(now_datetime(), -5)
        )

        with self.assertRaisesRegex(frappe.ValidationError, "Six months"):
            self.create_request()

    def test_scholarship_request_is_allowed_after_the_cooldowns(self):
        self.close_request(
            self.make_previous_request(),
            "Rejected",
            rejected_date=add_months(now_datetime(), -3) - timedelta(minutes=1),
        )
        self.assertTrue(self.create_request())

        self.close_request(
            self.get_last_request(),
            "Approved For Aid",
            approved_for_aid_date=add_months(now_datetime(), -6) - timedelta(minutes=1),
        )
        self.assertTrue(self.create_request())

    def test_approved_scholarship_request_blocks_the_next_request_for_six_months(self):
        scholarship_request = self.create_request()
        self.close_request(
            scholarship_request, "Approved For Aid", approved_for_aid_date=add_months(now_datetime(), -1)
        )

        with self.assertRaisesRegex(frappe.ValidationError, "Six months"):
            self.make_previous_request()

    def test_pending_scholarship_request_blocks_the_next_request(self):
        self.create_request()

        with self.assertRaisesRegex(frappe.ValidationError, "pending review"):
            self.make_previous_request()

    def make_previous_request(self) -> str:
        return (
            frappe.get_doc(
                {
                    "doctype": "Beneficiary Request",
                    "request_category": "Education Assistance",
                    "educational_assistance": "Tuition Fees",
                    "requested_amount": "1000",
                    "request_summary": "Tuition fees",
                }
            )
            .insert()
            .name
        )

    def close_request(self, request: str, state: str, **dates) -> None:
        frappe.db.set_value("Beneficiary Request", request, {"workflow_state": state, "status": state, **dates})

    def get_last_request(self) -> str:
        return frappe.get_last_doc("Beneficiary Request", filters={"beneficiaries": self.registration}).name


class TestAcceptedBeneficiaryScholarshipApproval(ScholarshipDecisionTestCase):
    def test_supervisor_approval_does_not_cascade_to_the_registration(self):
        frappe.set_user("Administrator")
        user = make_beneficiary_user()
        frappe.set_user(user)
        registration = make_registration(is_scholarship=0)
        accept_registration(registration, user)
        frappe.db.set_value("Beneficiaries Registration", registration, "ben_id", "123")
        create_scholarship_request(make_accepted_request_data())
        request = frappe.response["data"]["request"]
        frappe.set_user("Administrator")
        frappe.db.set_value("Beneficiary Request", request, "declaration", upload_declaration())
        frappe.set_user(self.supervisor)

        self.apply_request_action("Approve", request)

        self.assertEqual(
            frappe.db.get_value("Beneficiary Request", request, "workflow_state"), "Pending Specialist Approval"
        )
        self.assertEqual(frappe.db.get_value("Beneficiaries Registration", registration, "workflow_state"), "Accepted")
        self.assertNotIn("aids/beneficiary", self.sanadi.endpoints)
        subvention_body = self.sanadi.get_body("aids/subvention-request")
        self.assertEqual((subvention_body["benId"], subvention_body["aidLookupId"]), ("123", 1001050))

    def test_new_scholarship_request_does_not_lock_an_accepted_scholarship_registration(self):
        # An applicant accepted through an earlier scholarship applies again from /scholarship.
        frappe.set_user("Administrator")
        user = make_beneficiary_user()
        frappe.set_user(user)
        registration = make_registration(is_scholarship=1)
        accept_registration(registration, user)
        create_scholarship_request(make_accepted_request_data())
        frappe.set_user(self.supervisor)

        # apply_workflow reloads the registration, so the notes the rejection needs are stored first.
        frappe.db.set_value("Beneficiaries Registration", registration, "custom_notes", "Rejected by the Supervisor")
        apply_workflow(frappe.get_doc("Beneficiaries Registration", registration), "Reject")

        self.assertEqual(
            frappe.db.get_value("Beneficiaries Registration", registration, "workflow_state"), "Not Accepted"
        )


def make_accepted_request_data() -> dict:
    return {
        **make_request_data(),
        **{fieldname: upload_unattached_file(fieldname) for fieldname in SCHOLARSHIP_ATTACHMENT_FIELDS},
    }
