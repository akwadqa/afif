import frappe

from afif.afif.doctype.donation_project.donation_project import RESERVED_SLUGS, SLUG_MAX_LENGTH
from afif.donation_slug import get_english_title, get_unique_slug, slugify


def execute():
	# Projects without a usable English title fall back to their name so the patch never fails
	for project in frappe.get_all("Donation Project", filters={"slug": ["is", "not set"]}, fields=["name", "title"]):
		slug = slugify(get_english_title(project.title), SLUG_MAX_LENGTH) or project.name
		frappe.db.set_value(
			"Donation Project",
			project.name,
			"slug",
			get_unique_slug("Donation Project", slug, project.name, RESERVED_SLUGS),
			update_modified=False,
		)
