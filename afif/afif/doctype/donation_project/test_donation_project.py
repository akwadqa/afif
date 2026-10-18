# Copyright (c) 2026, Akwad and Contributors
# See license.txt

from contextlib import ExitStack
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from afif.afif.doctype.donation_project.donation_project import (
	AmountExceedsRemainingError,
	ProjectClosedError,
	credit_donation,
)
from afif.donation_api import create_donation


class TestDonationProject(FrappeTestCase):
	def setUp(self):
		program = frappe.get_doc({"doctype": "Donation Program", "title": "Test Program", "published": 1}).insert()
		self.project = frappe.get_doc(
			{
				"doctype": "Donation Project",
				"program": program.name,
				"title": "Test Project",
				"image": "/files/test-project.png",
				"published": 1,
				"required_amount": 1000,
			}
		).insert()

	def stub_payment(self):
		# create_donation commits before calling Dibsy; stub both so the test's rollback still applies
		stack = ExitStack()
		stack.enter_context(patch.object(frappe.db, "commit"))
		stack.enter_context(
			patch("afif.donation_api.dibsy.create_payment", return_value={"payment_url": "https://pay.test"})
		)
		return stack

	def get_project(self):
		return frappe.db.get_value(
			"Donation Project", self.project.name, ["donated_amount", "percentage", "status"], as_dict=True
		)

	def test_credit_counts_each_donation_once(self):
		credit_donation(self.project.name, 100)
		credit_donation(self.project.name, 150)

		project = self.get_project()
		self.assertEqual(project.donated_amount, 250)
		self.assertAlmostEqual(project.percentage, 25)
		self.assertEqual(project.status, "Open")

	def test_project_closes_when_target_is_met(self):
		credit_donation(self.project.name, 600)
		self.assertEqual(self.get_project().status, "Open")

		credit_donation(self.project.name, 400)
		self.assertEqual(self.get_project().status, "Closed")

	def test_raising_required_amount_reopens_project(self):
		credit_donation(self.project.name, 1000)
		self.project.reload()
		self.assertEqual(self.project.status, "Closed")

		self.project.required_amount = 2000
		self.project.save()
		self.assertEqual(self.project.status, "Open")

	def test_project_without_target_stays_open(self):
		self.project.required_amount = 0
		self.project.save()
		credit_donation(self.project.name, 500)
		self.assertEqual(self.get_project().status, "Open")

	def test_closed_project_rejects_donations(self):
		credit_donation(self.project.name, 1000)

		with self.assertRaises(ProjectClosedError):
			create_donation(self.project.name, 50, is_anonymous=1)
		self.assertFalse(frappe.db.exists("Donation", {"donation_project": self.project.name}))

	def test_amount_above_remaining_is_rejected(self):
		credit_donation(self.project.name, 700)

		with self.stub_payment(), self.assertRaises(AmountExceedsRemainingError):
			create_donation(self.project.name, 301, is_anonymous=1)
		self.assertEqual(frappe.local.response["message"], {"remaining_amount": 300})
		self.assertFalse(frappe.db.exists("Donation", {"donation_project": self.project.name}))

	def test_amount_equal_to_remaining_is_accepted(self):
		credit_donation(self.project.name, 700)

		with self.stub_payment():
			result = create_donation(self.project.name, 300, is_anonymous=1)
		self.assertEqual(result["payment_url"], "https://pay.test")

	def test_project_without_target_has_no_cap(self):
		self.project.required_amount = 0
		self.project.save()

		with self.stub_payment():
			result = create_donation(self.project.name, 50000, is_anonymous=1)
		self.assertEqual(result["payment_url"], "https://pay.test")
