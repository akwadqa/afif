# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder.functions import Coalesce, NullIf
from frappe.utils import flt, get_datetime, getdate

STATUSES = ("Paid", "Pending", "Failed")
TEXT_FILTERS = ("donor_name", "donor_mobile", "donor_email", "reference_id", "gateway_transaction_id")
EXACT_FILTERS = ("payment_status", "donation_project", "donation_frequency", "currency")

# Group By option -> (id field, title field, doctype) per nesting level
GROUP_LEVELS = {
	"Program": [("program", "program_title", "Donation Program")],
	"Project": [("project", "project_title", "Donation Project")],
	"Program > Project": [
		("program", "program_title", "Donation Program"),
		("project", "project_title", "Donation Project"),
	],
}


def execute(filters=None):
	filters = frappe._dict(filters or {})
	validate_filters(filters)

	donations = get_donations(filters)
	levels = GROUP_LEVELS.get(filters.group_by)
	data = group_donations(donations, levels) if levels else donations

	return get_columns(), data, get_message(donations, filters), None, get_summary(donations)


def validate_filters(filters):
	if not filters.from_date or not filters.to_date:
		frappe.throw(_("From Date and To Date are required"))
	if getdate(filters.from_date) > getdate(filters.to_date):
		frappe.throw(_("From Date cannot be after To Date"))


def get_donations(filters):
	donation = frappe.qb.DocType("Donation")
	project = frappe.qb.DocType("Donation Project")
	program_doc = frappe.qb.DocType("Donation Program")
	# Donation.donation_program is optional; fall back to the project's program
	program = Coalesce(NullIf(donation.donation_program, ""), project.program)

	date_field = donation.paid_at if filters.date_based_on == "Paid At" else donation.creation
	query = (
		frappe.qb.from_(donation)
		.left_join(project)
		.on(project.name == donation.donation_project)
		.left_join(program_doc)
		.on(program_doc.name == program)
		.select(
			donation.name,
			donation.creation,
			donation.paid_at,
			program.as_("program"),
			program_doc.title.as_("program_title"),
			donation.donation_project.as_("project"),
			project.title.as_("project_title"),
			donation.donor_name,
			donation.donor_mobile,
			donation.donor_email,
			donation.donation_frequency,
			donation.payment_status,
			donation.payment_method,
			donation.amount,
			donation.currency,
			donation.reference_id,
			donation.gateway_transaction_id,
		)
		.where(
			date_field.between(
				get_datetime(f"{filters.from_date} 00:00:00"),
				get_datetime(f"{filters.to_date} 23:59:59.999999"),
			)
		)
		.orderby(donation.creation, order=frappe.qb.desc)
	)

	if filters.donation_program:
		query = query.where(program == filters.donation_program)
	for field in EXACT_FILTERS:
		if filters.get(field):
			query = query.where(donation[field] == filters.get(field))
	if filters.is_anonymous in ("Yes", "No"):
		query = query.where(donation.is_anonymous == (1 if filters.is_anonymous == "Yes" else 0))
	for field in TEXT_FILTERS:
		value = (filters.get(field) or "").strip()
		if value:
			query = query.where(donation[field].like(f"%{value}%"))

	return query.run(as_dict=True)


def group_donations(donations, levels, parent=None, indent=0):
	"""Nest donations under group header rows (largest amount first), each carrying its subtotal.

	Every non-top-level row has `parent_group`, so the report's total row only sums top-level headers.
	"""
	field, title_field, doctype = levels[0]
	groups = {}
	for row in donations:
		groups.setdefault(row[field], []).append(row)

	data = []
	for group_id, rows in sorted(groups.items(), key=lambda g: -sum(flt(r.amount) for r in g[1])):
		key = f"{parent or ''}/{group_id or ''}"
		currencies = {r.currency for r in rows}
		title = rows[0][title_field] or group_id or _("Not Set")
		data.append(
			frappe._dict(
				name=f"{title} ({len(rows)})",
				is_group=1,
				group_doctype=doctype,
				group_id=group_id,
				indent=indent,
				parent_group=parent,
				amount=sum(flt(r.amount) for r in rows),
				currency=currencies.pop() if len(currencies) == 1 else None,
			)
		)
		if len(levels) > 1:
			data.extend(group_donations(rows, levels[1:], key, indent + 1))
		else:
			for row in rows:
				row.update(indent=indent + 1, parent_group=key)
				data.append(row)
	return data


def get_columns():
	return [
		{"label": _("Donation"), "fieldname": "name", "fieldtype": "Link", "options": "Donation", "width": 220},
		{"label": _("Date"), "fieldname": "creation", "fieldtype": "Datetime", "width": 160},
		{"label": _("Paid At"), "fieldname": "paid_at", "fieldtype": "Datetime", "width": 160},
		{"label": _("Program"), "fieldname": "program_title", "fieldtype": "Data", "width": 160},
		{"label": _("Project"), "fieldname": "project_title", "fieldtype": "Data", "width": 180},
		{"label": _("Donor Name"), "fieldname": "donor_name", "fieldtype": "Data", "width": 150},
		{"label": _("Mobile"), "fieldname": "donor_mobile", "fieldtype": "Data", "width": 130},
		{"label": _("Email"), "fieldname": "donor_email", "fieldtype": "Data", "width": 180},
		{"label": _("Frequency"), "fieldname": "donation_frequency", "fieldtype": "Data", "width": 100},
		{"label": _("Status"), "fieldname": "payment_status", "fieldtype": "Data", "width": 100},
		{"label": _("Payment Method"), "fieldname": "payment_method", "fieldtype": "Data", "width": 120},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "options": "currency", "width": 120},
		{"label": _("Currency"), "fieldname": "currency", "fieldtype": "Link", "options": "Currency", "width": 80},
		{"label": _("Reference ID"), "fieldname": "reference_id", "fieldtype": "Data", "width": 160},
		{"label": _("Gateway Txn ID"), "fieldname": "gateway_transaction_id", "fieldtype": "Data", "width": 160},
	]


def get_summary(donations):
	currencies = {r.currency for r in donations if r.currency}
	currency = currencies.pop() if len(currencies) == 1 else None

	def amount(status=None):
		return sum(flt(r.amount) for r in donations if status is None or r.payment_status == status)

	summary = [{"label": _("Total Donations"), "value": len(donations), "datatype": "Int", "indicator": "Blue"}]
	for status, indicator in zip(STATUSES, ("Green", "Orange", "Red"), strict=True):
		summary.append(
			{"label": _(status), "value": amount(status), "datatype": "Currency", "currency": currency, "indicator": indicator}
		)
	summary.append(
		{"label": _("Total Amount"), "value": amount(), "datatype": "Currency", "currency": currency, "indicator": "Blue"}
	)
	return summary


def get_message(donations, filters):
	if not filters.currency and len({r.currency for r in donations if r.currency}) > 1:
		return _(
			"Results include more than one currency, so the totals mix currencies. Set the Currency filter for accurate totals."
		)
	return None
