# Copyright (c) 2023, Akwad and Contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from afif.afif.doctype.beneficiary_request.beneficiary_request import SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS

HOUSING_ATTACHMENTS = {
	"rent_contract": "/files/test-rent-contract.pdf",
	"onwer_qid": "/files/test-owner-qid.pdf",
	"late_letter": "/files/test-late-letter.pdf",
}


def make_request(**fields):
	request = frappe.get_doc(
		{"doctype": "Beneficiary Request", "requested_amount": "1000", "request_summary": "Test", **fields}
	)
	request.flags.ignore_links = True
	return request


class TestBeneficiaryRequest(FrappeTestCase):
	def setUp(self):
		# The eligibility hook needs an Accepted registration for the session user, unrelated to attachments
		eligibility_patch = patch("afif.hooks_call.before_insert_request")
		eligibility_patch.start()
		self.addCleanup(eligibility_patch.stop)

	def test_medical_request_without_bill_is_rejected_with_label(self):
		request = make_request(request_category="Medical Assistance", medical_assistance="Medication")

		with self.assertRaisesRegex(frappe.ValidationError, "Medical Bill"):
			request.insert()

	def test_real_estate_purchase_requires_estate_document(self):
		request = make_request(
			request_category="Housing Assistance",
			housing_assistance="Real estate purchase",
			**HOUSING_ATTACHMENTS,
		)

		self.assertEqual(request.get_missing_required_attachments(), ["estate_pruchase"])
		self.assertRaises(frappe.ValidationError, request.insert)

		request.estate_pruchase = "/files/test-estate.pdf"
		request.insert()

	def test_all_missing_attachments_are_listed(self):
		request = make_request(request_category="Education Assistance", educational_assistance="Tuition Fees")

		self.assertEqual(request.get_missing_required_attachments(), ["education_invoice", "grade_transcript"])

	def test_scholarship_needs_no_invoice_or_transcript(self):
		request = make_request(request_category="Education Assistance", educational_assistance="Scholarship")

		self.assertEqual(request.get_missing_required_attachments(), [])

	def test_new_scholarship_request_requires_its_four_documents(self):
		# new_doc, as the scholarship endpoints use, marks the request as new before it is inserted.
		request = frappe.new_doc("Beneficiary Request")
		request.update(
			{
				"requested_amount": "1000",
				"request_summary": "Test",
				"request_category": "Education Assistance",
				"educational_assistance": "Scholarship",
				"is_scholarship": 1,
				"is_data_accuracy_declared": 1,
				"is_eligibility_check_accepted": 1,
			}
		)

		self.assertEqual(
			request.get_missing_scholarship_fields(),
			[request.meta.get_label(fieldname) for fieldname in SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS],
		)

		request.update(
			{fieldname: f"/private/files/test-{fieldname}.pdf" for fieldname in SCHOLARSHIP_REQUEST_ATTACHMENT_FIELDS}
		)
		self.assertEqual(request.get_missing_scholarship_fields(), [])

	def test_existing_incomplete_request_can_still_be_saved(self):
		request = make_request(request_category="Housing Assistance", housing_assistance="Rent support")
		request.flags.ignore_validate = True
		request.insert()

		request.reload()
		request.request_summary = "Updated by staff"
		request.save()
