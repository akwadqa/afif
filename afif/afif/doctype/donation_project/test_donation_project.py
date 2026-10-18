# Copyright (c) 2026, Akwad and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from afif.afif.doctype.donation_project.donation_project import credit_donation


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
			"Donation Project", self.project.name, ["donated_amount", "percentage"], as_dict=True
		)

	def test_credit_counts_each_donation_once(self):
		credit_donation(self.project.name, 100)
		credit_donation(self.project.name, 150)

		project = self.get_project()
		self.assertEqual(project.donated_amount, 250)
		self.assertAlmostEqual(project.percentage, 25)
