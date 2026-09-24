
# Copyright (c) 2023, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class BeneficiaryAid(Document):
	pass


@frappe.whitelist()
def send_bulk_sms(names, message):

	if isinstance(names, str):
		names = frappe.parse_json(names)

	if not names:
		frappe.throw(_("No records selected."))

	message = (message or "").strip()
	if not message:
		frappe.throw(_("Message cannot be empty."))


	frappe.has_permission("Beneficiary Aid", "read", throw=True)

	beneficiary_names = frappe.get_all(
		"Beneficiary Aid",
		filters={"name": ["in", names]},
		pluck="beneficiaries",
	)
	beneficiary_names = list({b for b in beneficiary_names if b})

	if not beneficiary_names:
		frappe.throw(_("No beneficiaries linked to the selected records."))

	contacts = frappe.get_all(
		"Beneficiaries Registration",
		filters={"name": ["in", beneficiary_names]},
		fields=["name", "en_name", "phone_number"],
	)

	numbers, skipped = [], []
	for c in contacts:
		if c.phone_number:
			numbers.append(c.phone_number)
		else:
			skipped.append(c.en_name or c.name)

	if not numbers:
		frappe.throw(_("None of the selected beneficiaries have a phone number on file."))

	from frappe.core.doctype.sms_settings.sms_settings import send_sms

	send_sms(receiver_list=numbers, msg=message, success_msg=False)

	frappe.msgprint(
		_("SMS queued for {0} recipient(s).").format(len(numbers))
		+ (
			"<br>" + _("Skipped (no phone number on file): {0}").format(", ".join(skipped))
			if skipped
			else ""
		),
		title=_("Bulk SMS"),
		indicator="green",
	)

	return {"sent": len(numbers), "skipped": skipped}