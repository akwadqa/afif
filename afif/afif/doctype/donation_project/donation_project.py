# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class DonationProject(Document):
	def validate(self):
		self.update_percentage()

	def update_percentage(self):
		if flt(self.required_amount) > 0:
			self.percentage = flt(self.donated_amount) / flt(self.required_amount) * 100
		else:
			self.percentage = 0


def credit_donation(project_name, amount):
	"""Atomically add a paid donation's amount to its project's Donated Amount
	and recompute Percentage Raised in the same statement.

	Both columns are updated in one UPDATE so they can never drift apart: a
	separate read-recompute-write for percentage would race with concurrent
	donations to the same project (e.g. overlapping webhook deliveries),
	since donated_amount's own increment is atomic but a later percentage
	write could still be based on a donated_amount snapshot that's already
	stale by the time it's saved.
	"""
	frappe.db.sql(
		"""
		UPDATE `tabDonation Project`
		SET donated_amount = COALESCE(donated_amount, 0) + %(amount)s,
		    percentage = CASE
		        WHEN COALESCE(required_amount, 0) > 0
		        THEN (COALESCE(donated_amount, 0) + %(amount)s) / required_amount * 100
		        ELSE 0
		    END
		WHERE name = %(project_name)s
		""",
		{"amount": flt(amount), "project_name": project_name},
	)
