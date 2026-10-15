# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document

# Qatar mobile numbers are 8 digits starting with 3, 5, 6 or 7
QATAR_MOBILE_PATTERN = re.compile(r"^\+974[3567]\d{7}$")
ANONYMOUS_DONOR_NAME = "فاعل خير"
DONOR_FIELDS = ("donor_name", "donor_mobile", "donor_email")


class Donation(Document):
	def before_insert(self):
		if not self.reference_id:
			self.reference_id = frappe.generate_hash(length=32)

	def validate(self):
		self.validate_donor_details()
		self.donor_name = (self.donor_name or "").strip() or ANONYMOUS_DONOR_NAME
		self.donor_mobile = self.normalize_mobile(self.donor_mobile)
		if self.amount is not None and self.amount <= 0:
			frappe.throw(_("Amount must be greater than zero"))

	def validate_donor_details(self):
		"""Name, mobile and email are required unless the donor chose to donate as a benefactor."""
		if self.is_anonymous:
			return
		# Only enforce on new donations or when donor details are edited, so status
		# updates (e.g. the Dibsy webhook) on older donations without donor details still save
		if not self.is_new() and not any(
			self.has_value_changed(field) for field in (*DONOR_FIELDS, "is_anonymous")
		):
			return
		missing = [
			self.meta.get_label(field) for field in DONOR_FIELDS if not (self.get(field) or "").strip()
		]
		if missing:
			frappe.throw(
				_("Please enter {0}, or mark the donation as Benefactor.").format(", ".join(_(m) for m in missing)),
				frappe.MandatoryError,
			)

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
			frappe.throw(_("Donor Mobile must be a valid Qatar mobile number: 8 digits starting with 3, 5, 6 or 7, e.g. 55512345"))
		return mobile
