import frappe

from afif.donation_slug import get_english_title, get_unique_slug, slugify


def execute():
	# Programs without a usable English title fall back to their name so the patch never fails
	for program in frappe.get_all("Donation Program", filters={"slug": ["is", "not set"]}, fields=["name", "title"]):
		slug = slugify(get_english_title(program.title)) or program.name
		frappe.db.set_value(
			"Donation Program",
			program.name,
			"slug",
			get_unique_slug("Donation Program", slug, program.name),
			update_modified=False,
		)
