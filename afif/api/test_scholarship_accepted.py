from datetime import timedelta
from unittest.mock import patch

import frappe
from frappe.model.workflow import apply_workflow
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, add_months, now_datetime

from afif.hooks_call import AccountRestrictedError
from afif.afif.doctype.beneficiary_request.beneficiary_request import IncompleteScholarshipRequestError
from afif.api.scholarship import create_scholarship_request
from afif.api.test_scholarship import (
    REQUEST_FILE_TARGETS,
    accept_registration,
    assert_documents_attached_to_request,
    assert_files_unattached,
    assert_no_registration_scholarship_documents,
    attach_file_to,
    make_beneficiary_user,
    make_normal_education_request,
    make_registration,
    make_request_data,
    replace_file,
    upload_unattached_file,
)
from afif.api.test_scholarship_decision import ScholarshipDecisionTestCase, make_supervisor_user, upload_declaration


class AcceptedBeneficiaryTestCase(IntegrationTestCase):
    def setUp(self):
        sanadi = patch("afif.hooks_call.requests.post", side_effect=AssertionError("Sanadi must not be called"))
        sanadi.start()
        self.addCleanup(sanadi.stop)
        self.addCleanup(frappe.set_user, "Administrator")

        self.user = make_beneficiary_user()
        frappe.set_user(self.user)
        self.registration = make_registration(is_scholarship=1)
        accept_registration(self.registration, self.user)

    def create_request(self, request_data: dict | None = None) -> str:
        create_scholarship_request(request_data or make_request_data())
        return frappe.response["data"]["request"]

    def get_request_count(self) -> int:
        return frappe.db.count("Beneficiary Request", {"beneficiaries": self.registration})


class TestAcceptedBeneficiaryScholarshipRequest(AcceptedBeneficiaryTestCase):
    def test_accepted_user_creates_a_scholarship_request_with_its_files_on_the_request(self):
        request_data = make_request_data()
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
        assert_documents_attached_to_request(self, request.name, request_data)
        assert_no_registration_scholarship_documents(self, self.registration)

    def test_incomplete_request_creates_nothing(self):
        request_data = make_request_data()
        cases = {
            "missing student id": {"student_id_copy": None},
            "missing invoice": {"education_invoice": None},
            "missing amount": {"requested_amount": None},
            "missing summary": {"request_summary": ""},
            "unchecked declaration": {"is_data_accuracy_declared": 0},
        }
        for case, override in cases.items():
            with self.subTest(case), self.assertRaises(IncompleteScholarshipRequestError):
                self.create_request({**request_data, **override})

        self.assertEqual(self.get_request_count(), 0)
        assert_files_unattached(self, request_data)

    def test_another_users_file_is_rejected(self):
        frappe.set_user("Administrator")
        frappe.set_user(make_beneficiary_user())
        other_file_url = upload_unattached_file("other-user")
        frappe.set_user(self.user)
        request_data = make_request_data()

        for target in REQUEST_FILE_TARGETS:
            with self.subTest(target), self.assertRaises(frappe.PermissionError):
                self.create_request(replace_file(request_data, target, other_file_url))

        self.assertEqual(self.get_request_count(), 0)
        assert_files_unattached(self, request_data)

    def test_a_file_already_attached_elsewhere_is_rejected(self):
        for target in REQUEST_FILE_TARGETS:
            attached_url = upload_unattached_file("attached-elsewhere")
            attach_file_to(attached_url, "Beneficiaries Registration", self.registration)

            with self.subTest(target), self.assertRaises(frappe.PermissionError):
                self.create_request(replace_file(make_request_data(), target, attached_url))

        self.assertEqual(self.get_request_count(), 0)

    def test_normal_flow_beneficiary_cannot_create_a_scholarship_request(self):
        frappe.set_user("Administrator")
        user = make_beneficiary_user()
        frappe.set_user(user)
        registration = make_registration(is_scholarship=0)
        accept_registration(registration, user)

        with self.assertRaises(frappe.PermissionError):
            self.create_request()

        self.assertFalse(frappe.db.exists("Beneficiary Request", {"beneficiaries": registration}))

    def test_not_accepted_user_cannot_create_a_scholarship_request(self):
        frappe.set_user("Administrator")
        user = make_beneficiary_user()
        frappe.set_user(user)
        registration = make_registration(is_scholarship=1)

        with self.assertRaises(frappe.PermissionError):
            self.create_request()

        self.assertFalse(frappe.db.exists("Beneficiary Request", {"beneficiaries": registration}))


class TestScholarshipRequestCooldowns(AcceptedBeneficiaryTestCase):
    """A pending request still blocks a scholarship request; the rejection and approval waits do not."""

    def test_pending_request_blocks_a_scholarship_request(self):
        self.make_previous_request()

        with self.assertRaisesRegex(frappe.ValidationError, "pending review"):
            self.create_request()

        self.assertEqual(self.get_request_count(), 1)

    def test_recent_rejection_does_not_block_a_scholarship_request(self):
        self.close_request(self.make_previous_request(), "Rejected", rejected_date=add_days(now_datetime(), -1))

        self.assertTrue(self.create_request())

    def test_recent_approval_does_not_block_a_scholarship_request(self):
        self.close_request(
            self.make_previous_request(), "Approved For Aid", approved_for_aid_date=add_days(now_datetime(), -1)
        )

        self.assertTrue(self.create_request())

    def test_recent_rejection_still_blocks_a_normal_request(self):
        frappe.set_user("Administrator")
        user = make_beneficiary_user()
        frappe.set_user(user)
        registration = make_registration(is_scholarship=0)
        accept_registration(registration, user)
        rejected_request = make_normal_education_request()
        self.close_request(rejected_request, "Rejected", rejected_date=add_days(now_datetime(), -1))

        with self.assertRaisesRegex(frappe.ValidationError, "Three months"):
            make_normal_education_request()

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

    def test_approved_scholarship_request_does_not_block_the_next_request(self):
        scholarship_request = self.create_request()
        self.close_request(
            scholarship_request, "Approved For Aid", approved_for_aid_date=add_days(now_datetime(), -1)
        )

        self.assertTrue(self.create_request())

    def test_pending_scholarship_request_blocks_the_next_request(self):
        self.create_request()

        with self.assertRaisesRegex(frappe.ValidationError, "pending review"):
            self.make_previous_request()

    def make_previous_request(self) -> str:
        return make_normal_education_request()

    def close_request(self, request: str, state: str, **dates) -> None:
        frappe.db.set_value("Beneficiary Request", request, {"workflow_state": state, "status": state, **dates})

    def get_last_request(self) -> str:
        return frappe.get_last_doc("Beneficiary Request", filters={"beneficiaries": self.registration}).name


class TestAcceptedBeneficiaryScholarshipApproval(ScholarshipDecisionTestCase):
    def test_supervisor_approval_does_not_cascade_to_the_registration(self):
        frappe.set_user("Administrator")
        user = make_beneficiary_user()
        frappe.set_user(user)
        registration = make_registration(is_scholarship=1)
        accept_registration(registration, user)
        frappe.db.set_value("Beneficiaries Registration", registration, "ben_id", "123")
        create_scholarship_request(make_request_data())
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
        create_scholarship_request(make_request_data())
        frappe.set_user(self.supervisor)

        # apply_workflow reloads the registration, so the notes the rejection needs are stored first.
        frappe.db.set_value("Beneficiaries Registration", registration, "custom_notes", "Rejected by the Supervisor")
        apply_workflow(frappe.get_doc("Beneficiaries Registration", registration), "Reject")

        self.assertEqual(
            frappe.db.get_value("Beneficiaries Registration", registration, "workflow_state"), "Not Accepted"
        )



class TestAccountRestriction(AcceptedBeneficiaryTestCase):
    def setUp(self):
        super().setUp()
        # Saving an Accepted registration runs create_new_beneficiary, which calls Sanadi.
        sanadi_sync = patch("afif.hooks_call.create_new_beneficiary")
        sanadi_sync.start()
        self.addCleanup(sanadi_sync.stop)

    def restrict(self) -> None:
        frappe.db.set_value("Beneficiaries Registration", self.registration, "is_account_restricted", 1)

    def is_restricted(self) -> int:
        return frappe.db.get_value("Beneficiaries Registration", self.registration, "is_account_restricted")

    def save_as(self, user: str, **values) -> None:
        frappe.set_user(user)
        registration = frappe.get_doc("Beneficiaries Registration", self.registration)
        registration.update(values)
        registration.save()

    def make_staff_user(self, role: str) -> str:
        frappe.set_user("Administrator")
        user = make_supervisor_user()
        if role != "Supervisor":
            frappe.db.delete("Has Role", {"parent": user, "role": "Supervisor"})
            frappe.get_doc("User", user).add_roles(role)
        return user

    def test_restricted_student_cannot_file_a_request(self):
        self.restrict()

        with self.assertRaises(AccountRestrictedError):
            create_scholarship_request(make_request_data())

        self.assertEqual(self.get_request_count(), 0)

    def test_beneficiary_save_keeps_the_restriction(self):
        self.restrict()

        self.save_as(self.user, is_account_restricted=0, guardian_mobile_number="55555555")

        self.assertEqual(self.is_restricted(), 1)

    def test_specialist_cannot_restrict(self):
        specialist = self.make_staff_user("Specialist")

        self.save_as(specialist, is_account_restricted=1)

        self.assertEqual(self.is_restricted(), 0)

    def test_supervisor_can_restrict(self):
        self.save_as(self.make_staff_user("Supervisor"), is_account_restricted=1)

        self.assertEqual(self.is_restricted(), 1)
