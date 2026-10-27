# Copyright (c) 2026, Akwad and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document

from afif.donation_order import sync_project_order

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class DonationProgram(Document):
	def onload(self):
		if not self.is_new():
			sync_project_order(self)

	def validate(self):
		self.set_slug()
		if not self.is_new():
			sync_project_order(self)

	def set_slug(self):
		if self.slug:
			self.slug = self.slug.strip().lower()
			if not SLUG_PATTERN.match(self.slug):
				frappe.throw(_("Slug may only contain lowercase letters, digits and single hyphens"))
			return

		slug = slugify(get_english_title(self.title))
		if not slug:
			frappe.throw(_("Enter a slug or add an English translation for the title"))
		self.slug = get_unique_slug(slug, self.name)


def get_english_title(title: str | None) -> str:
	# Titles are stored in Arabic; the English version lives in the Translation doctype
	if not title:
		return ""
	return frappe.db.get_value("Translation", {"source_text": title, "language": "en"}, "translated_text") or title


def slugify(text: str) -> str:
	return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


def get_unique_slug(slug: str, program_name: str | None) -> str:
	candidate, suffix = slug, 2
	while frappe.db.exists("Donation Program", {"slug": candidate, "name": ["!=", program_name or ""]}):
		candidate = f"{slug}-{suffix}"
		suffix += 1
	return candidate
