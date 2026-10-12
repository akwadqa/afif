# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from afif.donation_order import sync_project_order


class DonationProgram(Document):
	def onload(self):
		if not self.is_new():
			sync_project_order(self)

	def validate(self):
		if not self.is_new():
			sync_project_order(self)
