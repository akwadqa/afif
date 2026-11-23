# Copyright (c) 2026, Akwad and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from afif.patches.backfill_donation_arabic_content import execute, preview


def make_translation(source_text, translated_text, language="ar"):
	frappe.get_doc({
		"doctype": "Translation",
		"source_text": source_text,
		"translated_text": translated_text,
		"language": language,
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


def count_source(field, source, doctype="Donation Program"):
	return preview()[doctype][field].get(source, 0)


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

	def test_arabic_only_text_is_copied_into_the_arabic_field(self):
		program = make_program("Arabic Only Program")
		project = make_project(
			program,
			"Arabic Only Project",
			body="<p>نص عربي بلا ترجمة إنجليزية</p>",
			quote="Every drop counts",
		)

		execute()

		project.reload()
		self.assertEqual(project.body_ar, "<p>نص عربي بلا ترجمة إنجليزية</p>")
		self.assertEqual(project.body, "<p>نص عربي بلا ترجمة إنجليزية</p>")
		self.assertFalse(project.quote_ar)

	def test_translation_wins_over_arabic_source_text(self):
		program = make_program("Arabic Source With Translation", intro="<p>مقدمة عربية</p>")
		make_translation("<p>مقدمة عربية</p>", "<p>مقدمة مترجمة</p>")

		execute()

		program.reload()
		self.assertEqual(program.intro_ar, "<p>مقدمة مترجمة</p>")

	def test_preview_counts_each_source_without_writing_anything(self):
		translated_before = count_source("title", "translation")
		arabic_before = count_source("intro", "arabic_source")
		program = make_program("Preview Program", intro="<p>مقدمة عربية بلا ترجمة</p>")
		make_translation("Preview Program", "برنامج المعاينة")

		self.assertEqual(count_source("title", "translation"), translated_before + 1)
		self.assertEqual(count_source("intro", "arabic_source"), arabic_before + 1)
		program.reload()
		self.assertFalse(program.title_ar)
		self.assertFalse(program.intro_ar)

	def test_preview_counts_fields_it_cannot_fill(self):
		before = count_source("intro", "no_arabic_available")
		make_program("Preview Untranslatable", intro="<p>English intro with no translation</p>")

		self.assertEqual(count_source("intro", "no_arabic_available"), before + 1)

	def test_rich_text_written_only_in_arabic_is_copied_into_the_arabic_field(self):
		# The markup carries more Latin letters than the sentence carries Arabic ones
		arabic_rich_text = '<p style="text-align: right;"><strong>ساعدنا</strong></p>'
		program = make_program("Arabic Rich Text", intro=arabic_rich_text)
		stored = program.intro

		execute()

		program.reload()
		self.assertEqual(program.intro_ar, stored)
		self.assertEqual(program.intro, stored)

	def test_english_translation_is_restored_into_the_english_field(self):
		arabic_intro = "<p>مقدمة عربية في حقل الإنجليزية</p>"
		program = make_program("Arabic Base Program", intro=arabic_intro)
		make_translation(arabic_intro, "<p>An English intro</p>", language="en")

		execute()

		program.reload()
		self.assertEqual(program.intro, "<p>An English intro</p>")
		self.assertEqual(program.intro_ar, arabic_intro)

	def test_preview_counts_a_restored_english_field_separately(self):
		before = count_source("intro", "english_restored")
		arabic_intro = "<p>مقدمة عربية</p>"
		make_program("Preview Restore", intro=arabic_intro)
		make_translation(arabic_intro, "<p>An English intro</p>", language="en")

		self.assertEqual(count_source("intro", "english_restored"), before + 1)

	def test_preview_does_not_report_an_empty_field_as_missing_arabic(self):
		missing_before = count_source("intro", "no_arabic_available")
		empty_before = count_source("intro", "empty")
		make_program("Preview Empty Intro")

		self.assertEqual(count_source("intro", "no_arabic_available"), missing_before)
		self.assertEqual(count_source("intro", "empty"), empty_before + 1)

	def test_existing_arabic_text_is_not_overwritten(self):
		program = make_program("Backfill Existing Arabic", title_ar="عنوان محرر يدويا")
		make_translation("Backfill Existing Arabic", "ترجمة قديمة")

		execute()

		program.reload()
		self.assertEqual(program.title_ar, "عنوان محرر يدويا")
