import re

import frappe

ARABIC_LETTERS = re.compile(r"[؀-ۿ]")
LATIN_LETTERS = re.compile(r"[A-Za-z]")

# Arabic used to live in the Translation doctype, keyed by the English source text
TRANSLATED_FIELDS = {
	"Donation Program": ("title", "intro"),
	"Donation Project": ("title", "quote", "body"),
	"Donation Project Amount": ("label",),
}


def execute():
	for doctype, fields in TRANSLATED_FIELDS.items():
		for name, planned in get_planned_changes(doctype, fields):
			values = {f"{field}_ar": value for field, (value, _source) in planned.items()}
			frappe.db.set_value(doctype, name, values, update_modified=False)


def preview():
	"""Report what execute() would change, without writing. Safe to run on production.

	Returns {doctype: {field: {source: count}}}, where source is one of
	`translation`, `arabic_source`, `no_arabic_available` or `already_filled`.
	"""
	report = {}
	for doctype, fields in TRANSLATED_FIELDS.items():
		counts = {field: {} for field in fields}
		for _name, planned in get_planned_changes(doctype, fields, include_unchanged=True):
			for field, (_value, source) in planned.items():
				counts[field][source] = counts[field].get(source, 0) + 1
		report[doctype] = counts
	return report


def get_planned_changes(doctype, fields, include_unchanged=False):
	# The Arabic columns are missing when preview() runs on a database that predates them
	existing = set(frappe.db.get_table_columns(doctype))
	arabic_columns = [f"{field}_ar" for field in fields if f"{field}_ar" in existing]
	records = frappe.get_all(
		doctype,
		fields=["name", *fields, *arabic_columns],
		ignore_ifnull=False,
	)
	translations = get_arabic_translations(records, fields)
	for record in records:
		planned = plan_record(record, fields, translations, include_unchanged)
		if planned:
			yield record.name, planned


def plan_record(record, fields, translations, include_unchanged=False):
	"""{field: (arabic value, source)} for every field the patch would fill.

	Only empty fields are filled, so the patch can be re-run and never overwrites an edit.
	"""
	planned = {}
	for field in fields:
		if record.get(f"{field}_ar"):
			source = "already_filled"
			value = None
		elif translations.get(record.get(field)):
			source = "translation"
			value = translations[record.get(field)]
		elif get_arabic_source(record.get(field)):
			source = "arabic_source"
			value = record.get(field)
		else:
			source = "no_arabic_available"
			value = None
		if value or include_unchanged:
			planned[field] = (value, source)
	return planned


def get_arabic_source(text):
	"""A field written in Arabic with no English version belongs in the Arabic column.

	It is copied, not moved: the English column keeps showing it until someone writes the
	English text, and the Arabic version survives that edit.
	"""
	if not text or len(ARABIC_LETTERS.findall(text)) <= len(LATIN_LETTERS.findall(text)):
		return None
	return text


def get_arabic_translations(records, fields):
	sources = {record.get(field) for record in records for field in fields if record.get(field)}
	if not sources:
		return {}
	rows = frappe.get_all(
		"Translation",
		filters={"language": "ar", "source_text": ["in", list(sources)]},
		fields=["source_text", "translated_text"],
	)
	return {row.source_text: row.translated_text for row in rows}
