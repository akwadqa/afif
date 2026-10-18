# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

MAX_DONATION_AMOUNTS = 6

STATUS_OPEN = "Open"
STATUS_CLOSED = "Closed"


class ProjectClosedError(frappe.ValidationError):
	"""Raised when donating to a project that already met its target; the frontend matches on its name."""


class DonationProject(Document):
	def validate(self):
		self.update_percentage()
		self.update_status()
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

	def update_status(self):
		# Derived from the funding figures (same rule as credit_donation), so raising the
		# Required Amount on a closed project reopens it
		is_target_met = flt(self.required_amount) > 0 and flt(self.donated_amount) >= flt(self.required_amount)
		self.status = STATUS_CLOSED if is_target_met else STATUS_OPEN


def credit_donation(project_name, amount):
	"""Atomically add a paid donation's amount to its project's Donated Amount
	and recompute Percentage Raised and Status in the same statement.

	All columns are updated in one UPDATE so they can never drift apart: a
	separate read-recompute-write would race with concurrent donations to the
	same project (e.g. overlapping webhook deliveries).

	MariaDB evaluates single-table UPDATE assignments left to right, so the
	percentage and status expressions already see the incremented donated_amount.
	"""
	frappe.db.sql(
		"""
		UPDATE `tabDonation Project`
		SET donated_amount = COALESCE(donated_amount, 0) + %(amount)s,
		    percentage = CASE
		        WHEN COALESCE(required_amount, 0) > 0
		        THEN donated_amount / required_amount * 100
		        ELSE 0
		    END,
		    status = CASE
		        WHEN COALESCE(required_amount, 0) > 0 AND donated_amount >= required_amount
		        THEN %(closed)s
		        ELSE %(open)s
		    END
		WHERE name = %(project_name)s
		""",
		{"amount": flt(amount), "project_name": project_name, "open": STATUS_OPEN, "closed": STATUS_CLOSED},
	)
