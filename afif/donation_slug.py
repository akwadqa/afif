import re

import frappe
from frappe import _

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def set_slug(doc, max_length: int | None = None):
	"""Normalise a manually entered slug, or generate one from the English title.

	Like Frappe's website routes, a slug is generated once and never follows later title edits,
	so shared links keep working.
	"""
	if doc.slug:
		doc.slug = doc.slug.strip().lower()
		if not SLUG_PATTERN.match(doc.slug):
			frappe.throw(_("Slug may only contain lowercase letters, digits and single hyphens"))
	else:
		slug = slugify(get_english_title(doc.title), max_length)
		if not slug:
			frappe.throw(_("Enter a slug or add an English translation for the title"))
		doc.slug = get_unique_slug(doc.doctype, slug, doc.name)


def get_english_title(title: str | None) -> str:
	# Titles are stored in Arabic; the English version lives in the Translation doctype
	if not title:
		return ""
	return frappe.db.get_value("Translation", {"source_text": title, "language": "en"}, "translated_text") or title


def slugify(text: str, max_length: int | None = None) -> str:
	slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
	if max_length and len(slug) > max_length:
		# Cut at a word boundary so the slug doesn't end mid-word
		slug = slug[: max_length + 1].rsplit("-", 1)[0] if "-" in slug[:max_length] else slug[:max_length]
	return slug


def get_unique_slug(doctype: str, slug: str, name: str | None) -> str:
	candidate, suffix = slug, 2
	while frappe.db.exists(doctype, {"slug": candidate, "name": ["!=", name or ""]}):
		candidate = f"{slug}-{suffix}"
		suffix += 1
	return candidate
