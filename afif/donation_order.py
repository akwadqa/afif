# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

"""Admin-controlled display order for donation programs and projects.

Programs are ordered by the `program_order` table in Donation Display Settings, and each
program's projects by its `project_order` table. Admins only drag rows; the tables are
kept in sync with the real records here, and the API falls back to newest-first for
anything not (yet) in a table.
"""

import frappe


def sync_program_order(settings):
	_sync_order_table(settings, "program_order", "program", "Donation Program", {})


def sync_project_order(program):
	_sync_order_table(program, "project_order", "project", "Donation Project", {"program": program.name})


def _sync_order_table(doc, table_field, link_field, doctype, filters):
	"""Keep the admin's order, drop rows for records that are gone, append new records at the end."""
	records = {
		r.name: r
		for r in frappe.get_all(
			doctype, filters=filters, fields=["name", "title", "published"], order_by="creation desc"
		)
	}
	ordered = [row.get(link_field) for row in doc.get(table_field) if row.get(link_field) in records]
	ordered += [name for name in records if name not in ordered]

	doc.set(table_field, [])
	for name in ordered:
		record = records[name]
		doc.append(
			table_field,
			{link_field: name, f"{link_field}_title": record.title or name, "published": record.published},
		)


def get_program_positions():
	return {
		r.program: r.idx
		for r in frappe.get_all(
			"Donation Program Order",
			filters={"parenttype": "Donation Display Settings", "parentfield": "program_order"},
			fields=["program", "idx"],
		)
	}


def get_project_positions(programs=None):
	"""{(program, project): position} — keyed by program so a project moved elsewhere isn't misplaced."""
	filters = {"parenttype": "Donation Program", "parentfield": "project_order"}
	if programs is not None:
		filters["parent"] = ("in", programs or [""])
	return {
		(r.parent, r.project): r.idx
		for r in frappe.get_all("Donation Project Order", filters=filters, fields=["parent", "project", "idx"])
	}


def sort_by_position(items, position):
	"""Stable sort: positioned items first in table order, the rest keep their (newest-first) order."""
	items.sort(key=lambda item: (position(item) is None, position(item) or 0))
	return items
