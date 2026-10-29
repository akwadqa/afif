import json
from unittest.mock import MagicMock, patch

import frappe
from frappe.model.workflow import WorkflowTransitionError, apply_workflow
from frappe.tests import IntegrationTestCase
from frappe.utils import random_string

from afif.afif.doctype.beneficiaries_registration.beneficiaries_registration import ScholarshipDecisionError
from afif.afif.doctype.beneficiary_request.beneficiary_request import (
    SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS,
    ScholarshipCascadeError,
)
from afif.api.scholarship import submit_scholarship_application
from afif.api.test_scholarship import (
    accept_registration,
    make_beneficiary_user,
    make_pdf,
    make_normal_education_request_data,
    make_registration,
    make_request_data,
)
from afif.hooks_call import UnmappedAidLookupError, get_aid_lookup_parent_id, new_aid_request

# Other Educational Assistance, used for Scholarship until Sanadi has its own code (plan OQ6).
SCHOLARSHIP_AID_LOOKUP_ID = 1001050
SANADI_BEN_ID = 987
SANADI_REQUEST_ID = 555
# Fields create_new_beneficiary maps to Sanadi codes, which make_registration leaves empty.
SANADI_PROFILE = {
    "gender": "Male",
    "education_level": "High Education Level",
    "ben_requestor_relationtype": "The same subvention requestor",
    "city": "Doha",
}


class FakeSanadi:
    """Records every call and answers like the Sanadi endpoints the hooks use."""

    def __init__(self, failing_endpoint: str | None = None):
        self.failing_endpoint = failing_endpoint
        self.calls: list[tuple[str, dict]] = []

    def post(self, url: str, **kwargs):
        endpoint = url.split("/sanadi/", 1)[1].split("?", 1)[0]
        body = kwargs.get("data")
        self.calls.append((endpoint, json.loads(body) if isinstance(body, str) else body))
        if endpoint == self.failing_endpoint:
            return make_response(500, {"ms": "Sanadi failure"})
        return make_response(200, self.get_answer(endpoint))

    def get_answer(self, endpoint: str) -> dict:
        return {
            "auth/integration/login": {"rs": {"token": "test-token"}},
            "aids/subvention-request/search": {"count": 0},
            "aids/beneficiary": {"rs": {"first": "SAVED", "second": {"id": SANADI_BEN_ID}}},
            "aids/subvention-request": {
                "rs": {"id": SANADI_REQUEST_ID, "requestSerial": 1, "requestFullSerial": "TEST-1"}
            },
        }.get(endpoint, {})

    @property
    def endpoints(self) -> list[str]:
        return [endpoint for endpoint, _body in self.calls]

    def get_body(self, endpoint: str) -> dict:
        return next(body for called, body in self.calls if called == endpoint)


def make_response(status_code: int, body: dict) -> MagicMock:
    return MagicMock(status_code=status_code, json=MagicMock(return_value=body))


class ScholarshipDecisionTestCase(IntegrationTestCase):
    def setUp(self):
        self.sanadi = FakeSanadi()
        self.start_patch(patch("afif.hooks_call.requests.post", side_effect=self.sanadi.post))
        sanadi_settings = ("https://sanadi.test/", "q", "u", "p")
        self.start_patch(patch("afif.hooks_call.get_sanadi_integration_settings", return_value=sanadi_settings))
        self.addCleanup(frappe.set_user, "Administrator")

        self.applicant = make_beneficiary_user()
        frappe.set_user(self.applicant)
        self.registration = make_registration(is_scholarship=1)
        frappe.db.set_value("Beneficiaries Registration", self.registration, SANADI_PROFILE)
        submit_scholarship_application(self.registration, make_request_data())
        self.request = frappe.response["data"]["request"]

        frappe.set_user("Administrator")
        frappe.db.set_value("Beneficiary Request", self.request, "declaration", upload_declaration())
        self.supervisor = make_supervisor_user()
        frappe.set_user(self.supervisor)

    def start_patch(self, patcher):
        patcher.start()
        self.addCleanup(patcher.stop)

    def apply_request_action(self, action: str, request: str | None = None):
        return apply_workflow(frappe.get_doc("Beneficiary Request", request or self.request), action)

    def get_registration_state(self) -> str:
        return frappe.db.get_value("Beneficiaries Registration", self.registration, "workflow_state")

    def get_request_state(self) -> str:
        return frappe.db.get_value("Beneficiary Request", self.request, "workflow_state")


class TestScholarshipSupervisorDecision(ScholarshipDecisionTestCase):
    def test_approving_the_request_accepts_the_registration_first(self):
        self.apply_request_action("Approve")

        registration = frappe.get_doc("Beneficiaries Registration", self.registration)
        self.assertEqual((registration.workflow_state, registration.status), ("Accepted", "Accepted"))
        self.assertEqual(registration.ben_id, str(SANADI_BEN_ID))
        self.assertEqual(self.get_request_state(), "Pending Specialist Approval")
        self.assertEqual(frappe.db.get_value("Beneficiary Request", self.request, "request_id"), str(SANADI_REQUEST_ID))

        endpoints = self.sanadi.endpoints
        self.assertLess(endpoints.index("aids/beneficiary"), endpoints.index("aids/subvention-request"))
        subvention_body = self.sanadi.get_body("aids/subvention-request")
        self.assertEqual(subvention_body["benId"], str(SANADI_BEN_ID))
        self.assertEqual(
            (subvention_body["aidLookupParentId"], subvention_body["aidLookupId"]),
            (10010, SCHOLARSHIP_AID_LOOKUP_ID),
        )

    def test_rejecting_the_request_leaves_the_registration_as_it_is(self):
        self.apply_request_action("Reject")

        registration = frappe.get_doc("Beneficiaries Registration", self.registration)
        self.assertEqual((registration.workflow_state, registration.status), ("New Registration", "New Registration"))
        self.assertFalse(registration.custom_notes)
        self.assertEqual(self.get_request_state(), "Rejected by Supervisor")
        self.assertEqual(self.sanadi.calls, [])

    def test_sanadi_failure_while_accepting_changes_neither_document(self):
        cases = {
            # create_new_beneficiary throws on this one
            "beneficiary call fails": ("aids/beneficiary", frappe.ValidationError),
            # create_new_beneficiary only logs this one and leaves ben_id empty
            "authentication fails": ("auth/integration/login", ScholarshipCascadeError),
        }
        for case, (failing_endpoint, error) in cases.items():
            with self.subTest(case):
                self.sanadi.failing_endpoint = failing_endpoint
                frappe.db.savepoint("supervisor_approval")
                with self.assertRaises(error):
                    self.apply_request_action("Approve")
                # What the request handler does with the failed transaction.
                frappe.db.rollback(save_point="supervisor_approval")

                self.assertEqual(self.get_registration_state(), "New Registration")
                self.assertFalse(frappe.db.get_value("Beneficiaries Registration", self.registration, "ben_id"))
                self.assertEqual(self.get_request_state(), "Pending Supervisor Approval")
                self.assertFalse(frappe.db.get_value("Beneficiary Request", self.request, "request_id"))
                self.assertNotIn("aids/subvention-request", self.sanadi.endpoints)

    def test_approval_without_declaration_is_blocked(self):
        frappe.db.set_value("Beneficiary Request", self.request, "declaration", None)

        with self.assertRaises(WorkflowTransitionError):
            self.apply_request_action("Approve")

        self.assertEqual(self.get_registration_state(), "New Registration")
        self.assertEqual(self.sanadi.calls, [])

    def test_approval_with_unmapped_subcategory_fails_before_calling_sanadi(self):
        # A scholarship request always carries the Scholarship subcategory, so the missing mapping is simulated.
        unmapped = patch(
            "afif.afif.doctype.beneficiary_request.beneficiary_request.get_aid_lookup_parent_id",
            side_effect=UnmappedAidLookupError("Unmapped"),
        )

        with unmapped, self.assertRaises(UnmappedAidLookupError):
            self.apply_request_action("Approve")

        self.assertEqual(self.sanadi.calls, [])

    def test_desk_sanadi_id_check_lets_a_pending_scholarship_through(self):
        request = frappe.get_doc("Beneficiary Request", self.request)

        self.assertTrue(request.check_beneficiary_id()["success"])


class TestOlderScholarshipRequestDecision(ScholarshipDecisionTestCase):
    """Requests filed before the documents moved to the request (plan P9-4) hold none of them."""

    def setUp(self):
        super().setUp()
        frappe.db.set_value(
            "Beneficiary Request", self.request, dict.fromkeys(SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS)
        )

    def test_older_request_without_documents_can_be_approved(self):
        self.apply_request_action("Approve")

        self.assertEqual(self.get_request_state(), "Pending Specialist Approval")
        self.assertEqual(self.get_registration_state(), "Accepted")

    def test_older_request_without_documents_can_be_rejected(self):
        self.apply_request_action("Reject")

        self.assertEqual(self.get_request_state(), "Rejected by Supervisor")


class TestScholarshipRegistrationGuard(ScholarshipDecisionTestCase):
    def test_registration_cannot_be_decided_directly_while_its_request_is_pending(self):
        for action in ("Approve", "Reject"):
            with self.subTest(action), self.assertRaises(ScholarshipDecisionError):
                apply_workflow(frappe.get_doc("Beneficiaries Registration", self.registration), action)

        self.assertEqual(self.get_registration_state(), "New Registration")
        self.assertEqual(self.sanadi.calls, [])

    def test_after_the_request_is_rejected_the_registration_follows_its_own_workflow(self):
        self.apply_request_action("Reject")

        apply_workflow(frappe.get_doc("Beneficiaries Registration", self.registration), "Approve")

        self.assertEqual(self.get_registration_state(), "Accepted")
        self.assertEqual(self.get_request_state(), "Rejected by Supervisor")


class TestScholarshipAidLookup(ScholarshipDecisionTestCase):
    def test_scholarship_maps_to_education_and_its_own_lookup_id(self):
        request = frappe.get_doc("Beneficiary Request", self.request)

        self.assertEqual(get_aid_lookup_parent_id(request), (10010, SCHOLARSHIP_AID_LOOKUP_ID))

    def test_existing_education_mapping_is_unchanged(self):
        request = frappe._dict(request_category="Education Assistance", educational_assistance="Tuition Fees")

        self.assertEqual(get_aid_lookup_parent_id(request), (10010, 1001010))

    def test_unmapped_subcategory_raises_a_clear_error(self):
        cases = {
            "unknown subcategory": {"request_category": "Education Assistance", "educational_assistance": "Unknown"},
            "unknown category": {"request_category": "Unknown"},
        }
        for case, request in cases.items():
            with self.subTest(case), self.assertRaises(UnmappedAidLookupError):
                get_aid_lookup_parent_id(frappe._dict(request))

    def test_aid_for_a_scholarship_request_is_sent_with_the_scholarship_lookup_id(self):
        self.apply_request_action("Approve")
        aid = frappe._dict(
            workflow_state="Approved",
            beneficiary_request=self.request,
            doner_id="Doner",
            payment_periodicity="One Time",
            payment_date="2026-10-19",
            approval_date="2026-10-19",
            nb_installements=1,
            aid_amount=15000,
            suggested_amount=15000,
            disbursement_decision="Scholarship aid",
        )

        new_aid_request(aid, "on_update")

        aid_body = self.sanadi.get_body("aids/subvention-aid")
        self.assertEqual((aid_body["aidLookupParentId"], aid_body["aidLookupId"]), (10010, SCHOLARSHIP_AID_LOOKUP_ID))
        self.assertEqual(aid_body["subventionRequestId"], SANADI_REQUEST_ID)


class TestNormalRequestApprovalUnchanged(ScholarshipDecisionTestCase):
    def test_normal_request_rejection_does_not_touch_the_registration(self):
        frappe.set_user("Administrator")
        user = make_beneficiary_user()
        frappe.set_user(user)
        registration = make_registration(is_scholarship=0)
        accept_registration(registration, user)
        request = frappe.get_doc(make_normal_education_request_data()).insert()
        frappe.set_user(self.supervisor)

        self.apply_request_action("Reject", request.name)

        self.assertEqual(frappe.db.get_value("Beneficiary Request", request.name, "workflow_state"), "Rejected by Supervisor")
        self.assertEqual(frappe.db.get_value("Beneficiaries Registration", registration, "workflow_state"), "Accepted")

    def test_normal_request_approval_does_not_touch_the_registration(self):
        frappe.set_user("Administrator")
        user = make_beneficiary_user()
        frappe.set_user(user)
        registration = make_registration(is_scholarship=0)
        accept_registration(registration, user)
        frappe.db.set_value("Beneficiaries Registration", registration, "ben_id", "123")
        request = frappe.get_doc(make_normal_education_request_data()).insert()
        frappe.set_user("Administrator")
        frappe.db.set_value("Beneficiary Request", request.name, "declaration", upload_declaration())
        frappe.set_user(self.supervisor)

        self.apply_request_action("Approve", request.name)

        self.assertEqual(
            frappe.db.get_value("Beneficiary Request", request.name, "workflow_state"), "Pending Specialist Approval"
        )
        self.assertEqual(frappe.db.get_value("Beneficiaries Registration", registration, "workflow_state"), "Accepted")
        self.assertNotIn("aids/beneficiary", self.sanadi.endpoints)
        subvention_body = self.sanadi.get_body("aids/subvention-request")
        self.assertEqual((subvention_body["benId"], subvention_body["aidLookupId"]), ("123", 1001010))


def make_supervisor_user() -> str:
    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": f"scholarship-supervisor-{random_string(8).lower()}@example.com",
            "first_name": "Scholarship Supervisor",
            "send_welcome_email": 0,
            "roles": [{"role": "Supervisor"}],
        }
    ).insert(ignore_permissions=True)
    return user.name


def upload_declaration() -> str:
    file = frappe.get_doc(
        {"doctype": "File", "file_name": "declaration.pdf", "content": make_pdf(), "is_private": 1}
    ).insert()
    return file.file_url
