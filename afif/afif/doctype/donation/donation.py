# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document

QATAR_MOBILE_PATTERN = re.compile(r"^\+974\d{8}$")
ANONYMOUS_DONOR_NAME = "فاعل خير"


class Donation(Document):
	def before_insert(self):
		if not self.reference_id:
			self.reference_id = frappe.generate_hash(length=32)

	def validate(self):
		self.donor_name = (self.donor_name or "").strip() or ANONYMOUS_DONOR_NAME
		self.donor_mobile = self.normalize_mobile(self.donor_mobile)
		if self.amount is not None and self.amount <= 0:
			frappe.throw(_("Amount must be greater than zero"))

	def on_update(self):
		if self.payment_status == "Paid" and self.has_value_changed("payment_status"):
			from afif.afif.doctype.donation_project.donation_project import credit_donation

			credit_donation(self.donation_project, self.amount)

	@staticmethod
	def normalize_mobile(mobile):
		mobile = (mobile or "").strip().replace(" ", "")
		if not mobile:
			return ""
		if not mobile.startswith("+974") and mobile.isdigit() and len(mobile) == 8:
			mobile = f"+974{mobile}"
		if not QATAR_MOBILE_PATTERN.match(mobile):
			frappe.throw(_("Donor Mobile must be a valid Qatar number, e.g. +97455512345"))
		return mobile
