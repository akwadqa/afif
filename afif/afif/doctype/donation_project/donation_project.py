# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

MAX_DONATION_AMOUNTS = 6


class DonationProject(Document):
	def validate(self):
		self.update_percentage()
		self.validate_donation_amounts()

	def validate_donation_amounts(self):
		if len(self.donation_amounts) > MAX_DONATION_AMOUNTS:
			frappe.throw(_("A project can have at most {0} donation amounts").format(MAX_DONATION_AMOUNTS))

		seen = set()
		for row in self.donation_amounts:
			if flt(row.amount) <= 0:
				frappe.throw(_("Row #{0}: Amount must be greater than 0").format(row.idx))
			if flt(row.amount) in seen:
				frappe.throw(_("Row #{0}: Amount {1} is already listed").format(row.idx, row.amount))
			seen.add(flt(row.amount))

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
