# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

from afif import dibsy
from afif.afif.doctype.donation_project.donation_project import (
	STATUS_CLOSED,
	AmountExceedsRemainingError,
	ProjectClosedError,
)
from afif.donation_order import get_program_positions, get_project_positions, sort_by_position


PROGRAM_TEXT_FIELDS = ("title", "intro")
PROJECT_TEXT_FIELDS = ("title", "quote", "body")
AMOUNT_TEXT_FIELDS = ("label",)


def localize(record, fields, lang):
	"""Resolve each text to the requested language and drop the Arabic columns from the payload.

	An empty Arabic value falls back to English, so a half-translated record never renders blank.
	"""
	for field in fields:
		arabic = record.pop(f"{field}_ar", None)
		if lang == "ar" and arabic:
			record[field] = arabic


def with_arabic(*fields):
	return [name for field in fields for name in (field, f"{field}_ar")]


def _normalize_lang(lang):
	return lang if lang in ("ar", "en") else "ar"


PROGRESS_FIELDS = ("required_amount", "donated_amount", "percentage")


def _apply_progress_visibility(project):
	# Projects with Show Progress off don't expose their funding figures at all
	if not project.get("show_progress"):
		for field in PROGRESS_FIELDS:
			project[field] = None


def _attach_amounts(projects, lang):
	# One query for every project's preset amounts, kept in table (idx) order
	names = [p["name"] for p in projects]
	if not names:
		return
	rows = frappe.get_all(
		"Donation Project Amount",
		filters={"parenttype": "Donation Project", "parentfield": "donation_amounts", "parent": ["in", names]},
		fields=["parent", "amount", *with_arabic("label")],
		order_by="idx asc",
		ignore_permissions=True,
	)
	amounts = {}
	for row in rows:
		amount = {"amount": row.amount, "label": row.label, "label_ar": row.label_ar}
		localize(amount, AMOUNT_TEXT_FIELDS, lang)
		amounts.setdefault(row.parent, []).append(amount)
	for project in projects:
		project["amounts"] = amounts.get(project["name"], [])


@frappe.whitelist(allow_guest=True)
def get_programs(lang=None):
	lang = _normalize_lang(lang)

	programs = frappe.get_all(
		"Donation Program",
		filters={"published": 1},
		fields=["name", *with_arabic("title", "intro")],
		order_by="creation desc",
		ignore_permissions=True,
	)
	for program in programs:
		localize(program, PROGRAM_TEXT_FIELDS, lang)
	positions = get_program_positions()
	return sort_by_position(programs, lambda p: positions.get(p["name"]))


@frappe.whitelist(allow_guest=True)
def get_projects(program, lang=None):
	lang = _normalize_lang(lang)

	if not frappe.db.exists("Donation Program", {"name": program, "published": 1}):
		frappe.throw(_("Donation Program not found"), frappe.DoesNotExistError)

	projects = frappe.get_all(
		"Donation Project",
		filters={"program": program, "published": 1},
		fields=[
			"name",
			*with_arabic("title", "quote", "body"),
			"status",
			"show_progress",
			"required_amount",
			"donated_amount",
			"percentage",
		],
		order_by="creation desc",
		ignore_permissions=True,
	)
	for project in projects:
		localize(project, PROJECT_TEXT_FIELDS, lang)
		_apply_progress_visibility(project)
	_attach_amounts(projects, lang)
	positions = get_project_positions([program])
	return sort_by_position(projects, lambda p: positions.get((program, p["name"])))


@frappe.whitelist(allow_guest=True)
def get_donation_landing(lang=None):
	lang = _normalize_lang(lang)

	programs = frappe.get_all(
		"Donation Program",
		filters={"published": 1},
		fields=["name", "slug", "icon", *with_arabic("title", "intro")],
		order_by="creation desc",
		ignore_permissions=True,
	)
	program_positions = get_program_positions()
	sort_by_position(programs, lambda p: program_positions.get(p["name"]))
	project_positions = get_project_positions([p["name"] for p in programs])

	for program in programs:
		projects = frappe.get_all(
			"Donation Project",
			filters={"program": program["name"], "published": 1},
			fields=[
				"name",
				"slug",
				*with_arabic("title"),
				"image",
				"location",
				"status",
				"show_progress",
				"required_amount",
				"donated_amount",
				"percentage",
			],
			order_by="creation desc",
			ignore_permissions=True,
		)
		for project in projects:
			localize(project, ("title",), lang)
			_apply_progress_visibility(project)
		sort_by_position(projects, lambda p, program=program: project_positions.get((program["name"], p["name"])))

		localize(program, PROGRAM_TEXT_FIELDS, lang)
		program["projects"] = projects

	_attach_amounts([p for program in programs for p in program["projects"]], lang)
	return programs


@frappe.whitelist(allow_guest=True)
def get_project_detail(project_name=None, lang=None, slug=None):
	# Project pages use the slug; links shared before slugs existed still carry the name
	lang = _normalize_lang(lang)

	filters = {"slug": slug} if slug else {"name": project_name}
	project = frappe.db.get_value(
		"Donation Project",
		{**filters, "published": 1},
		[
			"name",
			"slug",
			*with_arabic("title", "quote", "body"),
			"image",
			"location",
			"status",
			"show_progress",
			"required_amount",
			"donated_amount",
			"percentage",
			"program",
		],
		as_dict=True,
	)
	if not project:
		frappe.throw(_("Donation Project not found"), frappe.DoesNotExistError)

	program = frappe.db.get_value(
		"Donation Program",
		project.program,
		["slug", "icon", *with_arabic("title", "intro")],
		as_dict=True,
	)

	localize(project, PROJECT_TEXT_FIELDS, lang)
	localize(program, PROGRAM_TEXT_FIELDS, lang)
	project["program_title"] = program.title
	project["program_intro"] = program.intro
	project["program_icon"] = program.icon
	project["program_slug"] = program.slug
	_apply_progress_visibility(project)
	_attach_amounts([project], lang)

	return project


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=10, seconds=60 * 60)
def create_donation(
	donation_project, amount, donor_name=None, donor_mobile=None, donor_email=None, is_anonymous=0
):
	project = frappe.db.get_value(
		"Donation Project",
		{"name": donation_project, "published": 1},
		["name", "status", "required_amount", "donated_amount"],
		as_dict=True,
	)
	if not project:
		frappe.throw(_("Donation Project not found"), frappe.DoesNotExistError)
	if project.status == STATUS_CLOSED:
		frappe.throw(
			_("This project has reached its required amount and is no longer accepting donations"),
			ProjectClosedError,
		)

	amount = frappe.utils.flt(amount)
	if amount <= 0:
		frappe.throw(_("Amount must be greater than 0"))

	remaining = frappe.utils.flt(
		frappe.utils.flt(project.required_amount) - frappe.utils.flt(project.donated_amount), 2
	)
	if frappe.utils.flt(project.required_amount) > 0 and amount > remaining:
		# Returned alongside the error so the frontend can show the limit in the donor's language,
		# even for projects that hide their funding figures
		frappe.local.response["message"] = {"remaining_amount": remaining}
		frappe.throw(
			_("The amount is greater than the {0} still needed for this project").format(remaining),
			AmountExceedsRemainingError,
		)

	donation = frappe.get_doc({
		"doctype": "Donation",
		"donation_project": project.name,
		"amount": amount,
		# Donor-detail rules (required unless benefactor, mobile format) live in Donation.validate
		"is_anonymous": frappe.utils.cint(is_anonymous),
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
		["name", "payment_status", "amount", "currency", "donor_name"],
		as_dict=True,
	)
	if not donation:
		frappe.throw(_("Donation not found"), frappe.DoesNotExistError)

	return donation
