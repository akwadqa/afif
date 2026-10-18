import frappe


def execute():
	# Close projects that already met their target, and correct percentages that
	# credit_donation previously over-counted
	for name in frappe.get_all("Donation Project", pluck="name"):
		project = frappe.get_doc("Donation Project", name)
		project.update_percentage()
		project.update_status()
		project.db_set(
			{"percentage": project.percentage, "status": project.status}, update_modified=False
		)
