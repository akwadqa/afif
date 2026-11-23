# Copyright (c) 2026, Akwad and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from afif.patches.backfill_donation_arabic_content import execute


def make_translation(source_text, translated_text):
	frappe.get_doc({
		"doctype": "Translation",
		"source_text": source_text,
		"translated_text": translated_text,
		"language": "ar",
	}).insert()


def make_program(title, **kwargs):
	return frappe.get_doc({"doctype": "Donation Program", "title": title, "published": 1, **kwargs}).insert()


def make_project(program, title, **kwargs):
	return frappe.get_doc({
		"doctype": "Donation Project",
		"program": program.name,
		"title": title,
		"image": "/files/test-project.png",
		"published": 1,
		**kwargs,
	}).insert()


class TestDonationArabicBackfill(FrappeTestCase):
	def test_program_title_and_intro_are_filled_from_translations(self):
		program = make_program("Backfill Program", intro="<p>Backfill program intro</p>")
		make_translation("Backfill Program", "برنامج التعبئة")
		make_translation("<p>Backfill program intro</p>", "<p>مقدمة البرنامج</p>")

		execute()

		program.reload()
		self.assertEqual(program.title_ar, "برنامج التعبئة")
		self.assertEqual(program.intro_ar, "<p>مقدمة البرنامج</p>")

	def test_project_title_quote_and_body_are_filled_from_translations(self):
		program = make_program("Backfill Project Program")
		project = make_project(
			program, "Backfill Project", quote="Backfill quote", body="<p>Backfill body</p>"
		)
		make_translation("Backfill Project", "مشروع التعبئة")
		make_translation("Backfill quote", "اقتباس التعبئة")
		make_translation("<p>Backfill body</p>", "<p>نص التعبئة</p>")

		execute()

		project.reload()
		self.assertEqual(project.title_ar, "مشروع التعبئة")
		self.assertEqual(project.quote_ar, "اقتباس التعبئة")
		self.assertEqual(project.body_ar, "<p>نص التعبئة</p>")

	def test_amount_label_is_filled_from_translation(self):
		program = make_program("Backfill Amount Program")
		project = make_project(
			program,
			"Backfill Amount Project",
			donation_amounts=[{"amount": 100, "label": "Backfill label"}],
		)
		make_translation("Backfill label", "وسم التعبئة")

		execute()

		project.reload()
		self.assertEqual(project.donation_amounts[0].label_ar, "وسم التعبئة")

	def test_record_without_translation_keeps_arabic_fields_empty(self):
		program = make_program("Backfill Untranslated", intro="<p>Untranslated intro</p>")

		execute()

		program.reload()
		self.assertFalse(program.title_ar)
		self.assertFalse(program.intro_ar)

	def test_existing_arabic_text_is_not_overwritten(self):
		program = make_program("Backfill Existing Arabic", title_ar="عنوان محرر يدويا")
		make_translation("Backfill Existing Arabic", "ترجمة قديمة")

		execute()

		program.reload()
		self.assertEqual(program.title_ar, "عنوان محرر يدويا")
