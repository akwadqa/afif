# Copyright (c) 2026, Akwad and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from afif.afif.doctype.donation_project.donation_project import credit_donation
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

		with self.assertRaises(frappe.ValidationError):
			create_donation(self.project.name, 50, is_anonymous=1)
		self.assertFalse(frappe.db.exists("Donation", {"donation_project": self.project.name}))
