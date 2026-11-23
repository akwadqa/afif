import re

import frappe

ARABIC_LETTERS = re.compile(r"[\u0600-\u06ff]")
LATIN_LETTERS = re.compile(r"[A-Za-z]")

# Arabic used to live in the Translation doctype, keyed by the English source text
TRANSLATED_FIELDS = {
	"Donation Program": ("title", "intro"),
	"Donation Project": ("title", "quote", "body"),
	"Donation Project Amount": ("label",),
}


def execute():
	for doctype, fields in TRANSLATED_FIELDS.items():
		records = frappe.get_all(
			doctype,
			fields=["name", *fields, *(f"{field}_ar" for field in fields)],
			ignore_ifnull=False,
		)
		translations = get_arabic_translations(records, fields)
		for record in records:
			backfill_record(doctype, record, fields, translations)


def backfill_record(doctype, record, fields, translations):
	# Only empty fields are filled, so the patch can be re-run and never overwrites an edit
	values = {}
	for field in fields:
		if record.get(f"{field}_ar"):
			continue
		arabic = translations.get(record.get(field)) or get_arabic_source(record.get(field))
		if arabic:
			values[f"{field}_ar"] = arabic
	if values:
		frappe.db.set_value(doctype, record.name, values, update_modified=False)


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
