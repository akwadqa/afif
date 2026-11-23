import re

import frappe

ARABIC_LETTERS = re.compile(r"[؀-ۿ]")
LATIN_LETTERS = re.compile(r"[A-Za-z]")
MARKUP = re.compile(r"<[^>]*>")

# Arabic used to live in the Translation doctype, keyed by the English source text
TRANSLATED_FIELDS = {
	"Donation Program": ("title", "intro"),
	"Donation Project": ("title", "quote", "body"),
	"Donation Project Amount": ("label",),
}


def execute():
	for doctype, fields in TRANSLATED_FIELDS.items():
		for name, planned in get_planned_changes(doctype, fields):
			values = {column: value for _field, (columns, _source) in planned.items() for column, value in columns.items()}
			frappe.db.set_value(doctype, name, values, update_modified=False)


def preview():
	"""Report what execute() would change, without writing. Safe to run on production.

	Returns {doctype: {field: {source: count}}}, where source is one of `translation`,
	`arabic_source`, `english_restored`, `no_arabic_available`, `empty` or `already_filled`.
	"""
	report = {}
	for doctype, fields in TRANSLATED_FIELDS.items():
		counts = {field: {} for field in fields}
		for _name, planned in get_planned_changes(doctype, fields, include_unchanged=True):
			for field, (_columns, source) in planned.items():
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
	translations = get_translations(records, fields)
	for record in records:
		planned = plan_record(record, fields, translations, include_unchanged)
		if planned:
			yield record.name, planned


def plan_record(record, fields, translations, include_unchanged=False):
	"""{field: ({column: value}, source)} for every field the patch would write."""
	planned = {}
	for field in fields:
		columns = plan_field(record, field, translations)
		source = describe_source(record, field, translations)
		if columns or include_unchanged:
			planned[field] = (columns, source)
	return planned


def plan_field(record, field, translations):
	"""The columns to write for one field.

	Only an empty Arabic column is filled, so the patch can be re-run and never
	overwrites an edit. A field written in Arabic while an English translation exists
	is split: each language ends up in its own column.
	"""
	text = record.get(field)
	columns = {}
	english = translations["en"].get(text) if is_written_in_arabic(text) else None
	if english:
		columns[field] = english
	if not record.get(f"{field}_ar"):
		arabic = translations["ar"].get(text) or (text if is_written_in_arabic(text) else None)
		if arabic:
			columns[f"{field}_ar"] = arabic
	return columns


def describe_source(record, field, translations):
	text = record.get(field)
	if is_written_in_arabic(text) and translations["en"].get(text):
		return "english_restored"
	if record.get(f"{field}_ar"):
		return "already_filled"
	if not text:
		return "empty"
	if translations["ar"].get(text):
		return "translation"
	if is_written_in_arabic(text):
		return "arabic_source"
	return "no_arabic_available"


def is_written_in_arabic(text):
	"""Whether the text itself is Arabic, ignoring the markup a Text Editor field carries.

	Tag names and attributes are Latin, and enough of them outweigh a short Arabic sentence.
	"""
	if not text:
		return False
	words = MARKUP.sub(" ", text)
	return len(ARABIC_LETTERS.findall(words)) > len(LATIN_LETTERS.findall(words))


def get_translations(records, fields):
	sources = {record.get(field) for record in records for field in fields if record.get(field)}
	if not sources:
		return {"ar": {}, "en": {}}
	rows = frappe.get_all(
		"Translation",
		filters={"language": ["in", ("ar", "en")], "source_text": ["in", list(sources)]},
		fields=["language", "source_text", "translated_text"],
	)
	translations = {"ar": {}, "en": {}}
	for row in rows:
		translations[row.language][row.source_text] = row.translated_text
	return translations
