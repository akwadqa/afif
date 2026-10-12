# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

from afif import dibsy
from afif.donation_order import get_program_positions, get_project_positions, sort_by_position


def _localize(text, lang):

	if not text:
		return text
	translated = frappe.db.get_value("Translation", {"source_text": text, "language": lang}, "translated_text")
	return translated or text


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
		fields=["parent", "amount", "label"],
		order_by="idx asc",
		ignore_permissions=True,
	)
	amounts = {}
	for row in rows:
		amounts.setdefault(row.parent, []).append({"amount": row.amount, "label": _localize(row.label, lang)})
	for project in projects:
		project["amounts"] = amounts.get(project["name"], [])


@frappe.whitelist(allow_guest=True)
def get_programs(lang=None):
	lang = _normalize_lang(lang)

	programs = frappe.get_all(
		"Donation Program",
		filters={"published": 1},
		fields=["name", "title", "intro"],
		order_by="creation desc",
		ignore_permissions=True,
	)
	for program in programs:
		program["title"] = _localize(program["title"], lang)
		program["intro"] = _localize(program["intro"], lang)
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
			"title",
			"quote",
			"body",
			"show_progress",
			"required_amount",
			"donated_amount",
			"percentage",
		],
		order_by="creation desc",
		ignore_permissions=True,
	)
	for project in projects:
		project["title"] = _localize(project["title"], lang)
		project["quote"] = _localize(project["quote"], lang)
		project["body"] = _localize(project["body"], lang)
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
		fields=["name", "title", "intro", "icon"],
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
				"title",
				"image",
				"location",
				"show_progress",
				"required_amount",
				"donated_amount",
				"percentage",
			],
			order_by="creation desc",
			ignore_permissions=True,
		)
		for project in projects:
			project["title"] = _localize(project["title"], lang)
			_apply_progress_visibility(project)
		sort_by_position(projects, lambda p, program=program: project_positions.get((program["name"], p["name"])))

		program["title"] = _localize(program["title"], lang)
		program["intro"] = _localize(program["intro"], lang)
		program["projects"] = projects

	_attach_amounts([p for program in programs for p in program["projects"]], lang)
	return programs


@frappe.whitelist(allow_guest=True)
def get_project_detail(project_name, lang=None):
	lang = _normalize_lang(lang)

	project = frappe.db.get_value(
		"Donation Project",
		{"name": project_name, "published": 1},
		[
			"name",
			"title",
			"quote",
			"body",
			"image",
			"location",
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
		["title", "intro", "icon"],
		as_dict=True,
	)

	project["title"] = _localize(project["title"], lang)
	project["quote"] = _localize(project["quote"], lang)
	project["body"] = _localize(project["body"], lang)
	project["program_title"] = _localize(program.title, lang)
	project["program_intro"] = _localize(program.intro, lang)
	project["program_icon"] = program.icon
	_apply_progress_visibility(project)
	_attach_amounts([project], lang)

	return project


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=10, seconds=60 * 60)
def create_donation(donation_project, amount, donor_name=None, donor_mobile=None, donor_email=None):
	project = frappe.db.get_value(
		"Donation Project",
		{"name": donation_project, "published": 1},
		["name"],
		as_dict=True,
	)
	if not project:
		frappe.throw(_("Donation Project not found"), frappe.DoesNotExistError)

	amount = frappe.utils.flt(amount)
	if amount <= 0:
		frappe.throw(_("Amount must be greater than 0"))

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
		["name", "payment_status", "amount", "currency", "donor_name"],
		as_dict=True,
	)
	if not donation:
		frappe.throw(_("Donation not found"), frappe.DoesNotExistError)

	return donation
