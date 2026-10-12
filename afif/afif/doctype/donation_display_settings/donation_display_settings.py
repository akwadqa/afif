# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from afif.donation_order import sync_program_order


class DonationDisplaySettings(Document):
	def onload(self):
		sync_program_order(self)

	def validate(self):
		sync_program_order(self)
