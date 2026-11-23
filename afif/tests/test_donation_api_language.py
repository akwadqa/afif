# Copyright (c) 2026, Akwad and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from afif.donation_api import get_donation_landing, get_programs, get_project_detail, get_projects


class TestDonationApiLanguage(FrappeTestCase):
	def setUp(self):
		self.program = frappe.get_doc({
			"doctype": "Donation Program",
			"title": "Water Wells",
			"title_ar": "آبار المياه",
			"intro": "<p>Clean water</p>",
			"intro_ar": "<p>مياه نظيفة</p>",
			"published": 1,
		}).insert()
		self.project = frappe.get_doc({
			"doctype": "Donation Project",
			"program": self.program.name,
			"title": "Deep Well",
			"title_ar": "بئر عميق",
			"quote": "Every drop counts",
			"quote_ar": "كل قطرة تهم",
			"body": "<p>Well details</p>",
			"body_ar": "<p>تفاصيل البئر</p>",
			"image": "/files/well.png",
			"published": 1,
			"required_amount": 1000,
			"donation_amounts": [{"amount": 100, "label": "One share", "label_ar": "سهم واحد"}],
		}).insert()

	def landing_program(self, lang=None):
		return next(p for p in get_donation_landing(lang=lang) if p["name"] == self.program.name)

	def test_arabic_request_returns_arabic_fields(self):
		program = self.landing_program(lang="ar")
		project = next(p for p in program["projects"] if p["name"] == self.project.name)

		self.assertEqual(program["title"], "آبار المياه")
		self.assertEqual(program["intro"], "<p>مياه نظيفة</p>")
		self.assertEqual(project["title"], "بئر عميق")
		self.assertEqual(project["amounts"][0]["label"], "سهم واحد")

	def test_english_request_returns_english_fields(self):
		program = self.landing_program(lang="en")
		project = next(p for p in program["projects"] if p["name"] == self.project.name)

		self.assertEqual(program["title"], "Water Wells")
		self.assertEqual(program["intro"], "<p>Clean water</p>")
		self.assertEqual(project["title"], "Deep Well")
		self.assertEqual(project["amounts"][0]["label"], "One share")

	def test_project_detail_resolves_both_languages(self):
		arabic = get_project_detail(slug=self.project.slug, lang="ar")
		english = get_project_detail(slug=self.project.slug, lang="en")

		self.assertEqual(arabic["title"], "بئر عميق")
		self.assertEqual(arabic["quote"], "كل قطرة تهم")
		self.assertEqual(arabic["body"], "<p>تفاصيل البئر</p>")
		self.assertEqual(arabic["program_title"], "آبار المياه")
		self.assertEqual(arabic["program_intro"], "<p>مياه نظيفة</p>")
		self.assertEqual(english["title"], "Deep Well")
		self.assertEqual(english["quote"], "Every drop counts")
		self.assertEqual(english["body"], "<p>Well details</p>")
		self.assertEqual(english["program_title"], "Water Wells")

	def test_list_endpoints_resolve_both_languages(self):
		arabic_program = next(p for p in get_programs(lang="ar") if p["name"] == self.program.name)
		english_program = next(p for p in get_programs(lang="en") if p["name"] == self.program.name)
		arabic_project = next(
			p for p in get_projects(self.program.name, lang="ar") if p["name"] == self.project.name
		)
		english_project = next(
			p for p in get_projects(self.program.name, lang="en") if p["name"] == self.project.name
		)

		self.assertEqual(arabic_program["title"], "آبار المياه")
		self.assertEqual(english_program["title"], "Water Wells")
		self.assertEqual(arabic_project["quote"], "كل قطرة تهم")
		self.assertEqual(english_project["quote"], "Every drop counts")

	def test_empty_arabic_field_falls_back_to_english(self):
		self.project.db_set("body_ar", "", update_modified=False)

		project = get_project_detail(slug=self.project.slug, lang="ar")

		self.assertEqual(project["body"], "<p>Well details</p>")
		self.assertEqual(project["title"], "بئر عميق")

	def test_missing_lang_defaults_to_arabic(self):
		self.assertEqual(self.landing_program()["title"], "آبار المياه")

	def test_response_never_exposes_the_arabic_field_names(self):
		program = self.landing_program(lang="ar")
		project = get_project_detail(slug=self.project.slug, lang="en")

		self.assertNotIn("title_ar", program)
		self.assertNotIn("intro_ar", program)
		self.assertNotIn("title_ar", program["projects"][0])
		self.assertNotIn("body_ar", project)
		self.assertNotIn("label_ar", project["amounts"][0])

	def test_translation_doctype_is_ignored(self):
		frappe.get_doc({
			"doctype": "Translation",
			"source_text": "Water Wells",
			"translated_text": "ترجمة قديمة",
			"language": "ar",
		}).insert()

		self.assertEqual(self.landing_program(lang="ar")["title"], "آبار المياه")
