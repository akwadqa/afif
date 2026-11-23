import frappe

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
	values = {
		f"{field}_ar": translations[record.get(field)]
		for field in fields
		if not record.get(f"{field}_ar") and translations.get(record.get(field))
	}
	if values:
		frappe.db.set_value(doctype, record.name, values, update_modified=False)


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
