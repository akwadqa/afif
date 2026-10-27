# Copyright (c) 2026, Akwad and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from afif.donation_api import get_donation_landing, get_project_detail


def make_program(title, slug=None):
	return frappe.get_doc(
		{"doctype": "Donation Program", "title": title, "slug": slug, "published": 1}
	).insert()


class TestDonationProgram(FrappeTestCase):
	def test_slug_is_generated_from_english_translation(self):
		frappe.get_doc(
			{"doctype": "Translation", "source_text": "برنامج اختبار", "translated_text": "Slug Test & Care", "language": "en"}
		).insert()

		self.assertEqual(make_program("برنامج اختبار").slug, "slug-test-care")

	def test_arabic_title_without_translation_or_slug_is_rejected(self):
		with self.assertRaisesRegex(frappe.ValidationError, "English translation"):
			make_program("عنوان بلا ترجمة")

	def test_manual_slug_with_invalid_format_is_rejected(self):
		with self.assertRaisesRegex(frappe.ValidationError, "Slug may only contain"):
			make_program("Slug Format", slug="bad slug!")

	def test_manual_slug_is_normalised(self):
		self.assertEqual(make_program("Slug Format", slug=" Mixed-Case ").slug, "mixed-case")

	def test_generated_slug_gets_suffix_on_collision(self):
		first = make_program("Slug Collision")
		second = make_program("Slug Collision")

		self.assertEqual(second.slug, f"{first.slug}-2")

	def test_existing_slug_is_kept_when_title_changes(self):
		program = make_program("Slug Stable")
		program.title = "Slug Renamed"
		program.save()

		self.assertEqual(program.slug, "slug-stable")

	def test_apis_return_program_slug(self):
		program = make_program("Slug Api")
		project = frappe.get_doc(
			{
				"doctype": "Donation Project",
				"program": program.name,
				"title": "Slug Api Project",
				"image": "/files/test-project.png",
				"published": 1,
				"required_amount": 1000,
			}
		).insert()

		self.assertEqual(get_project_detail(project.name, "en")["program_slug"], "slug-api")
		landing_program = next(p for p in get_donation_landing("en") if p["name"] == program.name)
		self.assertEqual(landing_program["slug"], "slug-api")
		self.assertEqual(landing_program["projects"][0]["program_slug"], "slug-api")
