# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

from afif import dibsy


@frappe.whitelist(allow_guest=True)
def get_programs():
	return frappe.get_all(
		"Donation Program",
		filters={"published": 1},
		fields=["name", "title", "intro", "display_order"],
		order_by="display_order asc, title asc",
		ignore_permissions=True,
	)


@frappe.whitelist(allow_guest=True)
def get_projects(program):
	if not frappe.db.exists("Donation Program", {"name": program, "published": 1}):
		frappe.throw(_("Donation Program not found"), frappe.DoesNotExistError)

	return frappe.get_all(
		"Donation Project",
		filters={"program": program, "published": 1},
		fields=["name", "title", "quote", "body", "min_amount", "display_order"],
		order_by="display_order asc, title asc",
		ignore_permissions=True,
	)


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=10, seconds=60 * 60)
def create_donation(donation_project, amount, donor_name, donor_mobile, donor_email=None):
	project = frappe.db.get_value(
		"Donation Project",
		{"name": donation_project, "published": 1},
		["name", "min_amount"],
		as_dict=True,
	)
	if not project:
		frappe.throw(_("Donation Project not found"), frappe.DoesNotExistError)

	amount = frappe.utils.flt(amount)
	if amount < frappe.utils.flt(project.min_amount):
		frappe.throw(_("Amount must be at least {0}").format(project.min_amount))

	donation = frappe.get_doc({
		"doctype": "Donation",
		"donation_project": project.name,
		"amount": amount,
		"donor_name": donor_name,
		"donor_mobile": donor_mobile,
		"donor_email": donor_email,
	})
	donation.insert(ignore_permissions=True)
	frappe.db.commit()

	checkout = dibsy.create_payment(donation)

	return {
		"reference_id": donation.reference_id,
		"amount": donation.amount,
		"currency": donation.currency,
		"payment_url": checkout["payment_url"],
	}


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=30, seconds=60 * 60)
def get_status(reference_id):
	donation = frappe.db.get_value(
		"Donation",
		{"reference_id": reference_id},
		["payment_status", "amount", "currency", "donor_name"],
		as_dict=True,
	)
	if not donation:
		frappe.throw(_("Donation not found"), frappe.DoesNotExistError)

	return donation
